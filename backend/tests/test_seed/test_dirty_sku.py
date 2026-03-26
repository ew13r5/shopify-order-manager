from seed.dirty_sku_generator import ZERO_WIDTH_CHARS, contaminate_sku, maybe_contaminate


def _strip_zero_width(s):
    """Remove all zero-width characters from string."""
    for char in ZERO_WIDTH_CHARS:
        s = s.replace(char, "")
    return s


class TestContaminateSku:
    def test_inserts_zero_width_chars(self):
        result = contaminate_sku("ABC-123")
        assert len(result) > len("ABC-123")
        assert _strip_zero_width(result) == "ABC-123"

    def test_output_differs_from_input(self):
        result = contaminate_sku("WIDGET-001")
        assert result != "WIDGET-001"
        assert _strip_zero_width(result) == "WIDGET-001"

    def test_inserts_from_known_set(self):
        original = "TEST-SKU"
        result = contaminate_sku(original)
        inserted = []
        orig_idx = 0
        for ch in result:
            if orig_idx < len(original) and ch == original[orig_idx]:
                orig_idx += 1
            else:
                inserted.append(ch)
        for ch in inserted:
            assert ch in ZERO_WIDTH_CHARS, f"Unexpected char: {repr(ch)}"

    def test_empty_string(self):
        assert contaminate_sku("") == ""


class TestMaybeContaminate:
    def test_contamination_rate(self):
        total = 1000
        contaminated = 0
        for i in range(total):
            sku = f"SKU-{i:04d}"
            result = maybe_contaminate(sku, rate=0.2)
            if result != sku:
                contaminated += 1
        ratio = contaminated / total
        assert 0.1 < ratio < 0.3, f"Expected ~20% contamination, got {ratio:.1%}"

    def test_rate_zero_no_contamination(self):
        for _ in range(100):
            result = maybe_contaminate("CLEAN", rate=0.0)
            assert result == "CLEAN"

    def test_rate_one_always_contaminates(self):
        for _ in range(100):
            result = maybe_contaminate("DIRTY", rate=1.0)
            assert result != "DIRTY"
