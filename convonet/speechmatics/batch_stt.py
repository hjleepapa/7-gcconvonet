"""
Speechmatics batch STT (v2 Jobs API). STT only — no TTS.
Requires SPEECHMATICS_API_KEY (Bearer token).
"""
import json
import logging
import os
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

BASE = "https://asr.api.speechmatics.com/v2/jobs"


def transcribe_speechmatics_batch(wav_bytes: bytes, language: str = "en") -> Optional[str]:
    """
    Transcribe mono WAV (16-bit PCM). Prefer 16 kHz+; pass output of voice_audio_util.to_wav_mono_16k.
    """
    api_key = (os.getenv("SPEECHMATICS_API_KEY") or "").strip()
    if not api_key:
        logger.error("SPEECHMATICS_API_KEY not set")
        return None
    if not wav_bytes or len(wav_bytes) < 500:
        return None

    lang = (language or "en").split("-")[0].lower()
    config = {
        "type": "transcription",
        "transcription_config": {"language": lang},
    }
    try:
        r = requests.post(
            BASE,
            headers={"Authorization": f"Bearer {api_key}"},
            data={"config": json.dumps(config)},
            files={"data_file": ("audio.wav", wav_bytes, "audio/wav")},
            timeout=60,
        )
        if r.status_code not in (200, 201):
            logger.error("Speechmatics job create failed: %s %s", r.status_code, r.text[:500])
            return None
        job_id = (r.json() or {}).get("id")
        if not job_id:
            logger.error("Speechmatics: no job id in response")
            return None

        deadline = time.time() + 120
        while time.time() < deadline:
            st = requests.get(
                f"{BASE}/{job_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30,
            )
            if st.status_code != 200:
                time.sleep(1)
                continue
            status = (st.json() or {}).get("job", {}).get("status") or st.json().get("status")
            if status in ("done", "completed"):
                break
            if status in ("rejected", "failed"):
                logger.error("Speechmatics job failed: %s", st.text[:500])
                return None
            time.sleep(0.8)

        tr = requests.get(
            f"{BASE}/{job_id}/transcript",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"format": "txt"},
            timeout=60,
        )
        if tr.status_code != 200:
            logger.error("Speechmatics transcript fetch failed: %s", tr.text[:500])
            return None
        text = (tr.text or "").strip()
        logger.info("Speechmatics STT ok: %s chars", len(text))
        return text or None
    except Exception as e:
        logger.exception("Speechmatics STT error: %s", e)
        return None
