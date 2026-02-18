"""
Rime TTS Service - Real-time Text-to-Speech
WebSocket-based streaming TTS using Rime's Arcana model
"""

import os
import logging
import asyncio
import threading
from typing import Optional, Callable, List
import subprocess
from queue import Queue, Empty
import io

logger = logging.getLogger(__name__)

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("websockets not available")


class RimeTTSService:
    """
    Real-time TTS using Rime's WebSocket API
    Supports streaming text input and audio output
    """
    
    def __init__(
        self,
        speaker: str = "astra",
        model_id: str = "arcana",
        audio_format: str = "wav"
    ):
        """
        Initialize Rime TTS service
        
        Args:
            speaker: Voice speaker (e.g., "astra", "ballad", etc.)
            model_id: Model ID (default: "arcana")
            audio_format: Audio format (default: "wav")
        """
        self.api_key = os.getenv('RIME_API_KEY')
        self.speaker = speaker
        self.model_id = model_id
        self.audio_format = audio_format
        # Request 48kHz to match LiveKit - default (22.05kHz) played at 48kHz sounds 2x too fast
        self.sampling_rate = 48000
        self.url = f"wss://users-ws.rime.ai/ws?speaker={speaker}&modelId={model_id}&audioFormat={audio_format}&samplingRate={self.sampling_rate}"
        self.auth_headers = {
            "Authorization": f"Bearer {self.api_key}"
        } if self.api_key else {}
        
        # Audio output buffer
        self.audio_data = b''
        self.output_queue: Queue = Queue()
        
    async def _synthesize_async(self, text_tokens: List[str]) -> bytes:
        """
        Synthesize speech from text tokens using WebSocket
        
        Args:
            text_tokens: List of text tokens to synthesize
            
        Returns:
            Raw PCM bytes (16-bit LE) at 48kHz
        """
        if not self.api_key:
            raise ValueError("RIME_API_KEY not set")
        
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets library required")
        
        audio_data = b''
        
        try:
            logger.info(f"🎵 Rime TTS: Connecting to {self.speaker} speaker")
            
            async with websockets.connect(self.url, additional_headers=self.auth_headers) as websocket:
                # Send text tokens
                logger.debug(f"📤 Sending {len(text_tokens)} tokens to Rime")
                for token in text_tokens:
                    try:
                        await websocket.send(token)
                    except Exception as send_error:
                        logger.error(f"❌ Error sending token: {send_error}")
                        raise
                
                # Receive audio chunks
                logger.debug("📥 Receiving audio from Rime")
                while True:
                    try:
                        audio_chunk = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        audio_data += audio_chunk
                        logger.debug(f"📥 Received audio chunk: {len(audio_chunk)} bytes")
                    except asyncio.TimeoutError:
                        logger.info("✅ Rime TTS stream complete (timeout)")
                        break
                    except websockets.exceptions.ConnectionClosedOK:
                        logger.info("✅ Rime WebSocket closed normally")
                        break
                    except Exception as recv_error:
                        logger.error(f"❌ Error receiving audio: {recv_error}")
                        break
            
            logger.info(f"✅ Rime TTS synthesis complete: {len(audio_data)} bytes")
            # Strip WAV header and return raw PCM - LiveKit expects PCM at 48kHz
            return self._wav_to_pcm(audio_data)
            
        except Exception as e:
            logger.error(f"❌ Rime TTS error: {type(e).__name__}: {e}")
            raise
    
    def synthesize(self, text: str, speaker: Optional[str] = None) -> bytes:
        """
        Synthesize speech from text (synchronous wrapper)
        
        Args:
            text: Text to synthesize
            speaker: Override speaker (optional)
            
        Returns:
            Raw PCM bytes (16-bit LE) at 48kHz for LiveKit
        """
        if speaker:
            self.speaker = speaker
            self.url = f"wss://users-ws.rime.ai/ws?speaker={speaker}&modelId={self.model_id}&audioFormat={self.audio_format}&samplingRate={self.sampling_rate}"
        
        # Split text into tokens (word-by-word with spaces)
        # Rime expects tokens to be sent individually
        tokens = self._tokenize_text(text)
        tokens.append("<EOS>")  # End of stream marker
        
        logger.info(f"🎤 Rime TTS: Synthesizing '{text[:50]}...' ({len(tokens)} tokens)")
        
        try:
            # Run async synthesis in event loop
            audio = asyncio.run(self._synthesize_async(tokens))
            return audio
        except RuntimeError as e:
            # Handle case where event loop already exists (Flask context)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Use thread-based approach if loop is already running
                    audio = self._synthesize_threaded(tokens)
                    return audio
            except:
                pass
            raise
    
    def _synthesize_threaded(self, tokens: List[str]) -> bytes:
        """
        Synthesize speech in a separate thread (for when event loop is running)
        
        Args:
            tokens: List of text tokens
            
        Returns:
            Raw PCM bytes (16-bit LE) at 48kHz
        """
        audio_result = []
        exception_result = []
        
        def run_in_new_loop():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audio = loop.run_until_complete(self._synthesize_async(tokens))
                audio_result.append(audio)
            except Exception as e:
                exception_result.append(e)
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_in_new_loop, daemon=False)
        thread.start()
        thread.join(timeout=60.0)  # 60 second timeout
        
        if exception_result:
            raise exception_result[0]
        
        if not audio_result:
            raise RuntimeError("Rime TTS synthesis timeout or failed")
        
        return audio_result[0]
    
    @staticmethod
    def _wav_to_pcm(wav_bytes: bytes, target_sr: int = 48000) -> bytes:
        """Strip WAV header, return raw PCM at target_sr. Resamples if WAV sample rate differs."""
        if len(wav_bytes) < 44:
            return wav_bytes
        if wav_bytes[:4] != b"RIFF" or b"WAVE" not in wav_bytes[:12]:
            return wav_bytes
        import struct
        # WAV fmt: bytes 24-27 = sample rate (little-endian)
        actual_sr = struct.unpack("<I", wav_bytes[24:28])[0]
        pcm = wav_bytes[44:]
        if actual_sr == target_sr:
            return pcm
        # Resample to 48kHz for LiveKit
        try:
            import numpy as np
            from scipy import signal
            audio = np.frombuffer(pcm, dtype=np.int16)
            ratio = target_sr / actual_sr
            num_samples = int(len(audio) * ratio)
            resampled = signal.resample(audio, num_samples)
            return np.clip(resampled, -32768, 32767).astype(np.int16).tobytes()
        except ImportError:
            logger.warning("scipy not available, returning PCM at original rate - may sound wrong")
            return pcm

    @staticmethod
    def _tokenize_text(text: str) -> List[str]:
        """
        Tokenize text into word tokens with spaces
        Rime expects word-level tokens
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Simple word tokenization - split by spaces
        words = text.split()
        
        # Add spaces between words (except last)
        tokens = []
        for i, word in enumerate(words):
            tokens.append(word)
            if i < len(words) - 1:
                tokens.append(" ")
        
        return tokens
    
    def get_speaker_list(self) -> List[str]:
        """
        Get available Rime speakers
        
        Returns:
            List of speaker names
        """
        # Common Rime speakers
        return [
            "astra",      # Female
            "ballad",     # Female
            "clint",      # Male
            "helen",      # Female
            "marcus",     # Male
            "scott",      # Male
        ]


# Singleton instance
_rime_service: Optional[RimeTTSService] = None


def get_rime_service(speaker: str = "astra") -> RimeTTSService:
    """Get or create Rime TTS service instance"""
    global _rime_service
    
    if _rime_service is None:
        _rime_service = RimeTTSService(speaker=speaker)
    elif _rime_service.speaker != speaker:
        # Update speaker if different
        _rime_service.speaker = speaker
        _rime_service.url = f"wss://users-ws.rime.ai/ws?speaker={speaker}&modelId={_rime_service.model_id}&audioFormat={_rime_service.audio_format}&samplingRate={_rime_service.sampling_rate}"
    
    return _rime_service


# REST API wrapper (for use in routes)
def rime_tts_synthesize(text: str, speaker: str = "astra") -> bytes:
    """
    Convenience function to synthesize speech
    
    Args:
        text: Text to synthesize
        speaker: Speaker to use
        
    Returns:
        Audio bytes in WAV format
    """
    service = get_rime_service(speaker)
    return service.synthesize(text, speaker=speaker)
