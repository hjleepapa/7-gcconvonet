"""Detect when the user wants the Hanok Table restaurant assistant."""


def detect_hanok_table_intent(text: str) -> bool:
    """
    Return True if the user is asking about restaurant reservations, Korean dining
    booking, Hanok Table, or typical reservation vocabulary.
    """
    if not text:
        return False
    t = text.strip().lower()

    keywords = [
        "hanok table",
        "hanok",
        "kfood",
        "k-food",
        "korean restaurant",
        "book a table",
        "book table",
        "dinner reservation",
        "lunch reservation",
        "make a reservation",
        "my reservation",
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
        if kw in t:
            print(f"🍽️ Hanok Table intent: matched '{kw}' in prompt", flush=True)
            return True

    print(f"📝 No Hanok Table intent in: {t!r}", flush=True)
    return False
