"""
Speechmatics Text-to-Speech (preview HTTP API).

Uses the same Bearer token as batch STT: SPEECHMATICS_API_KEY.

Voice: SPEECHMATICS_TTS_VOICE — sarah | theo | megan | jack (default sarah).
Output: WAV 16 kHz mono (use mime audio/wav in the voice WebSocket).

We use HTTP only (``requests``) so voice-gateway does not require the optional
``speechmatics-tts`` package. See Speechmatics TTS quickstart:
https://docs.speechmatics.com/text-to-speech/quickstart
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_PREVIEW_TTS_BASE = "https://preview.tts.speechmatics.com/generate"


def _allowed_voice() -> str:
    v = (os.getenv("SPEECHMATICS_TTS_VOICE") or "sarah").strip().lower()
    if v in ("sarah", "theo", "megan", "jack"):
        return v
    logger.warning("SPEECHMATICS_TTS_VOICE=%r invalid; using sarah", v)
    return "sarah"


def synthesize_speechmatics_tts(text: str) -> Optional[bytes]:
    """
    Return WAV bytes (16 kHz) or None on failure.
    """
    if not text or not str(text).strip():
        return None
    api_key = (os.getenv("SPEECHMATICS_API_KEY") or "").strip()
    if not api_key:
        logger.error("SPEECHMATICS_API_KEY not set (required for Speechmatics TTS)")
        return None

    voice = _allowed_voice()
    url = f"{_PREVIEW_TTS_BASE}/{voice}"
    try:
        r = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"text": text},
            timeout=120,
        )
        if r.status_code != 200:
            logger.error(
                "Speechmatics TTS HTTP failed: %s %s",
                r.status_code,
                (r.text or "")[:500],
            )
            return None
        data = r.content
        if not data or len(data) < 100:
            logger.error("Speechmatics TTS: empty or tiny response")
            return None
        logger.info("Speechmatics TTS: %s bytes voice=%s", len(data), voice)
        return data
    except Exception as e:
        logger.exception("Speechmatics TTS error: %s", e)
        return None
