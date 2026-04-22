"""Detect when the user wants the Hanok Table restaurant assistant."""

import re


def detect_hanok_table_intent(text: str) -> bool:
    """
    Return True if the user is asking about restaurant reservations, Korean dining
    booking, Hanok Table, or typical reservation vocabulary.
    """
    if not text:
        return False
    t = text.strip().lower()
    # Normalize punctuation/spacing so STT variants like "cancel my, reservation"
    # still match reservation intents.
    normalized = re.sub(r"[^a-z0-9]+", " ", t).strip()

    keywords = [
        "hanok table",
        "hanoek table",
        "hanoktable",
        "hanoek",
        "hanok",
        "kfood",
        "k-food",
        "korean restaurant",
        "restaurant reservation",
        "restaurant reservations",
        "book a table",
        "book table",
        "dinner reservation",
        "lunch reservation",
        "make a reservation",
        "make reservation",
        "my reservation",
        "reservations",
        "cancel reservation",
        "change reservation",
        "preorder",
        "pre-order",
        "bibimbap reservation",
        "party size",
        "waitlist",
        "confirmation code",
        "hnk-",
        "bulgogi order",
        "kimchi jjigae",
        "reserve at hanok",
    ]

    for kw in keywords:
        if kw in t or kw in normalized:
            print(f"🍽️ Hanok Table intent: matched '{kw}' in prompt", flush=True)
            return True

    action_words = r"(cancel|change|modify|update|reschedule|book|reserve|make)"
    reservation_words = r"(reservation|reservations|booking|bookings|table)"
    if re.search(action_words + r"(?:\s+\w+){0,5}\s+" + reservation_words, normalized):
        print(
            f"🍽️ Hanok Table intent: matched reservation action pattern in prompt {normalized!r}",
            flush=True,
        )
        return True
    if re.search(reservation_words + r"(?:\s+\w+){0,5}\s+" + action_words, normalized):
        print(
            f"🍽️ Hanok Table intent: matched reservation+action pattern in prompt {normalized!r}",
            flush=True,
        )
        return True

    print(f"📝 No Hanok Table intent in: {t!r}", flush=True)
    return False
