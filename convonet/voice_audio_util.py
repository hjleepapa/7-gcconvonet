"""
Convert browser audio (WebM/Opus) to WAV for STT providers that need PCM/WAV.
Requires ffmpeg (installed in voice-gateway Docker image).
"""
import logging
import os
import subprocess
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

WEBM_MAGIC = b"\x1a\x45\xdf\xa3"


def _ffmpeg_to_wav(audio_bytes: bytes, sample_rate: int, channels: int = 1) -> Optional[bytes]:
    if not audio_bytes or len(audio_bytes) < 100:
        return None
    suffix = ".webm" if (len(audio_bytes) >= 4 and audio_bytes[:4] == WEBM_MAGIC) else ".bin"
    inp = None
    outp = None
    fd = -1
    try:
        fd, inp = tempfile.mkstemp(suffix=suffix)
        os.write(fd, audio_bytes)
        os.close(fd)
        fd = -1
        outp = inp + ".out.wav"
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            inp,
            "-ar",
            str(sample_rate),
            "-ac",
            str(channels),
            "-f",
            "wav",
            outp,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=120, check=False)
        if r.returncode != 0 or not os.path.isfile(outp):
            logger.warning("ffmpeg failed: %s", (r.stderr or b"")[:500])
            return None
        with open(outp, "rb") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("ffmpeg not found; install ffmpeg for ElevenLabs/Cartesia/Speechmatics STT with WebM input")
        return None
    except Exception as e:
        logger.warning("audio convert error: %s", e)
        return None
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except Exception:
                pass
        for p in (inp, outp):
            if p and os.path.isfile(p):
                try:
                    os.unlink(p)
                except Exception:
                    pass


def to_wav_mono_16k(audio_bytes: bytes) -> Optional[bytes]:
    """WebM or arbitrary input -> 16 kHz mono WAV (Speechmatics, ElevenLabs Scribe)."""
    return _ffmpeg_to_wav(audio_bytes, 16000, 1)


def pcm_s16le_mono_48k_from_audio(audio_bytes: bytes) -> Optional[bytes]:
    """Raw PCM s16le mono 48kHz for Cartesia batch STT (matches their _pcm_to_wav)."""
    wav = _ffmpeg_to_wav(audio_bytes, 48000, 1)
    if not wav:
        return None
    import io
    import wave

    try:
        with wave.open(io.BytesIO(wav), "rb") as w:
            if w.getnchannels() != 1 or w.getsampwidth() != 2:
                return None
            return w.readframes(w.getnframes())
    except Exception as e:
        logger.warning("wav parse error: %s", e)
        return None
