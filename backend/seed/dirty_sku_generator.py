import random

ZERO_WIDTH_CHARS = [
    "\u200B",  # zero-width space
    "\u200C",  # zero-width non-joiner
    "\u200D",  # zero-width joiner
    "\uFEFF",  # BOM / zero-width no-break space
    "\u00AD",  # soft hyphen
    "\u00A0",  # non-breaking space
]


def contaminate_sku(clean_sku: str) -> str:
    """Insert 1-3 zero-width Unicode characters at random positions."""
    if not clean_sku:
        return clean_sku
    chars_to_insert = random.randint(1, 3)
    result = list(clean_sku)
    for _ in range(chars_to_insert):
        char = random.choice(ZERO_WIDTH_CHARS)
        pos = random.randint(0, len(result))
        result.insert(pos, char)
    return "".join(result)


def maybe_contaminate(clean_sku: str, rate: float = 0.2) -> str:
    """Contaminate the SKU with probability `rate`.

    Returns the original SKU unchanged (1-rate) of the time.
    """
    if random.random() < rate:
        return contaminate_sku(clean_sku)
    return clean_sku
