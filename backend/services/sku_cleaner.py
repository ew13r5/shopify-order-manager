import unicodedata
from typing import Optional

ZERO_WIDTH_CHARS = "\u200B\u200C\u200D\uFEFF"
SOFT_HYPHEN = "\u00AD"
NBSP = "\u00A0"


def clean_sku(raw_sku: Optional[str]) -> Optional[str]:
    """Clean SKU by removing hidden Unicode characters.

    Pipeline: NFKC normalize -> strip zero-width -> strip invisible -> trim.
    """
    if raw_sku is None:
        return None

    result = unicodedata.normalize("NFKC", raw_sku)

    for ch in ZERO_WIDTH_CHARS:
        result = result.replace(ch, "")

    result = result.replace(SOFT_HYPHEN, "")
    result = result.replace(NBSP, " ")
    result = result.strip()

    return result


def has_hidden_chars(raw_sku: Optional[str]) -> bool:
    """Returns True if the SKU contains hidden Unicode characters."""
    if raw_sku is None:
        return False
    return raw_sku != clean_sku(raw_sku)
