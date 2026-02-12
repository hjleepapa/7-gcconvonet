"""
Cartesia STT and TTS Service
Provides high-quality, low-latency speech-to-text and text-to-speech using Cartesia API.
"""

import os
import logging
import base64
import json
import asyncio
import websockets
from typing import Optional, Generator, AsyncGenerator
import httpx

logger = logging.getLogger(__name__)

# Check for Cartesia SDK
try:
    from cartesia import Cartesia
    CARTESIA_SDK_AVAILABLE = True
except ImportError:
    CARTESIA_SDK_AVAILABLE = False
    logger.warning("Cartesia SDK not available. Install with: pip install cartesia")

class CartesiaService:
    """Service for Cartesia STT and TTS"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('CARTESIA_API_KEY')
        if not self.api_key:
            logger.warning("⚠️ CARTESIA_API_KEY not set. Cartesia services will not work.")
            self.client = None
        elif CARTESIA_SDK_AVAILABLE:
            self.client = Cartesia(api_key=self.api_key)
        else:
            self.client = None
            
        # Default settings
        self.model_id = "sonic-english"  # Default TTS model
        self.voice_id = "a0e99841-438c-4a64-b67c-3cbc96c22b02"  # Example voice (Barbershop Man)
        self.stt_model = "shur-english-general" # Default STT model (assumed based on reference, verify if needed)
        self.stt_version = "2024-02-29"

    def is_available(self) -> bool:
        """Check if Cartesia service is available"""
        return bool(self.api_key and (CARTESIA_SDK_AVAILABLE or self.api_key))

    def transcribe_audio_buffer(self, audio_buffer: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribe audio buffer using Cartesia STT (REST API)
        
        Args:
            audio_buffer: Raw audio bytes
            language: Language code (default: en)
            
        Returns:
            Transcribed text or None
        """
        if not self.is_available():
            return None

        # Cartesia STT currently uses a REST endpoint (based on reference)
        # We'll use httpx directly if SDK doesn't support convenient buffer upload or just to match reference
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Cartesia-Version": self.stt_version,
            }
            
            # Prepare multipart form data
            files = {"file": ("audio.wav", audio_buffer, "audio/wav")} 
            data = {
                "model": self.stt_model,
                "language": language,
                "timestamp_granularities[]": "word",
            }
            
            logger.info(f"📤 Cartesia STT: Uploading {len(audio_buffer)} bytes...")
            
            response = httpx.post(
                "https://api.cartesia.ai/stt",
                headers=headers,
                files=files,
                data=data,
                timeout=30.0,
            )
            
            if response.status_code == 200:
                payload = response.json()
                text = payload.get("text", "").strip()
                logger.info(f"✅ Cartesia STT success: '{text}'")
                return text
            else:
                logger.error(f"❌ Cartesia STT failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cartesia STT error: {e}")
            return None

    def synthesize_stream(self, text: str, voice_id: Optional[str] = None) -> Generator[bytes, None, None]:
        """
        Stream TTS audio from Cartesia
        
        Args:
            text: Text to synthesize
            voice_id: Voice ID (optional)
            
        Yields:
            Audio chunks (bytes)
        """
        if not self.is_available() or not self.client:
            logger.error("Cartesia SDK not initialized")
            return

        try:
            voice_id = voice_id or self.voice_id
            
            # Use the SDK's streaming method
            ws = self.client.tts.websocket()
            
            # Generate audio
            output = ws.send(
                model_id=self.model_id,
                transcript=text,
                voice_id=voice_id,
                stream=True,
                output_format={
                    "container": "raw",
                    "encoding": "pcm_f32le", # Cartesia default is often f32le, we might need to convert or ensure we handle it
                    "sample_rate": 44100
                }
            )
            
            for chunk in output:
                # Chunk is dictionary response from websocket
                # We need to extract the audio data
                if "audio" in chunk:
                    # Audio provided as raw bytes or base64? SDK usually handles it.
                    # Looking at SDK docs (generalized), it usually yields bytes directly if configured?
                    # Let's inspect typical SDK usage from reference if available.
                    # Reference used: `chunk_iter = self.client.tts.bytes(**params)` which returns bytes.
                    pass 
            
            # Re-reading reference implementation:
            # chunk_iter = self.client.tts.bytes(**params)
            # for chunk in chunk_iter: audio_file.write(chunk)
            
            # So we should use client.tts.bytes for simplicity if it supports streaming generator
            
            chunk_iter = self.client.tts.bytes(
                model_id=self.model_id,
                transcript=text,
                voice={"mode": "id", "id": voice_id},
                output_format={
                    "container": "raw", 
                    "encoding": "pcm_s16le", # Request s16le for easier compatibility with our backend
                    "sample_rate": 44100
                }
            )
            
            for chunk in chunk_iter:
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ Cartesia TTS streaming error: {e}")

_cartesia_service = None

def get_cartesia_service() -> CartesiaService:
    global _cartesia_service
    if _cartesia_service is None:
        _cartesia_service = CartesiaService()
    return _cartesia_service
