from services.sku_cleaner import clean_sku, has_hidden_chars


class TestCleanSku:
    def test_none_input(self):
        assert clean_sku(None) is None

    def test_clean_sku_unchanged(self):
        assert clean_sku("ABC-123") == "ABC-123"

    def test_removes_zero_width_space(self):
        assert clean_sku("SKU\u200B-001") == "SKU-001"

    def test_removes_zero_width_non_joiner(self):
        assert clean_sku("SKU\u200C-001") == "SKU-001"

    def test_removes_zero_width_joiner(self):
        assert clean_sku("SKU\u200D-001") == "SKU-001"

    def test_removes_bom(self):
        assert clean_sku("\uFEFFSKU-001") == "SKU-001"

    def test_removes_soft_hyphen(self):
        assert clean_sku("SKU\u00AD-001") == "SKU-001"

    def test_replaces_nbsp_with_space(self):
        assert clean_sku("SKU\u00A0001") == "SKU 001"

    def test_nfkc_normalization(self):
        # ﬁ (U+FB01) normalizes to "fi"
        assert clean_sku("\ufb01lter") == "filter"

    def test_trims_whitespace(self):
        assert clean_sku("  SKU-001  ") == "SKU-001"

    def test_multiple_contaminations(self):
        result = clean_sku("\u200BSKU\u200C-\u200D001\uFEFF")
        assert result == "SKU-001"


class TestHasHiddenChars:
    def test_contaminated_returns_true(self):
        assert has_hidden_chars("SKU\u200B-001") is True

    def test_clean_returns_false(self):
        assert has_hidden_chars("SKU-001") is False

    def test_none_returns_false(self):
        assert has_hidden_chars(None) is False
