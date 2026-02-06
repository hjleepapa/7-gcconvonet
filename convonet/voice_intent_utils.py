"""
Voice intent utilities for Convonet voice experiences.
Currently supports detecting when a caller explicitly requests a transfer
to a human agent so we only bridge when the caller asks for it.
"""

from __future__ import annotations

from typing import Iterable

# Keywords the caller can say to request a human agent/transfer.
# Keep phrases lowercase for simple substring matching on normalized input.
TRANSFER_KEYWORDS: tuple[str, ...] = (
    "transfer",
    "transfer call",
    "transfer this call",
    "transfer me",
    "connect me",
    "connect me to a human",
    "connect me to an agent",
    "connect me to someone",
    "human agent",
    "human representative",
    "human operator",
    "human person",
    "human",
    "live agent",
    "live person",
    "agent",
    "operator",
    "talk to someone",
    "talk to a human",
    "talk to an agent",
    "speak to someone",
    "speak to a human",
    "speak to an agent",
    "talk to support",
    "speak to support",
    "transport this call",
    "move this call",
    "customer service",
    "representative",
)


def normalize_text(text: str | None) -> str:
    """Normalize incoming text for keyword checks."""
    if not text:
        return ""
    return text.strip().lower()


def has_transfer_intent(
    text: str | None,
    custom_keywords: Iterable[str] | None = None,
) -> bool:
    """
    Return True if the caller explicitly asked to speak with a human agent.

    Args:
        text: Caller’s utterance/transcript.
        custom_keywords: Optional iterable of additional keywords/phrases.
    """
    normalized = normalize_text(text)
    if not normalized:
        return False

    keywords = TRANSFER_KEYWORDS
    if custom_keywords:
        keywords = tuple(set(TRANSFER_KEYWORDS).union(k.lower() for k in custom_keywords))

    return any(keyword in normalized for keyword in keywords)

