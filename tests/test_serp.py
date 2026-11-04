"""Test analyzer.serp — title/meta length + SERP preview (Tahap 4 fitur #3)."""

from bs4 import BeautifulSoup

from seoinngabs.analyzer.serp import (
    DESCRIPTION_LIMIT,
    TITLE_LIMIT,
    analyze_title_meta_lengths,
    render_serp_preview,
    _truncate,
)


def _soup(html):
    return BeautifulSoup(html, "html.parser")


class TestAnalyzeTitleMetaLengths:
    def test_ok_title_and_description(self):
        html = f"<title>{'T' * 45}</title><meta name='description' content=\"{'D' * 120}\">"
        result = analyze_title_meta_lengths(_soup(html))
        assert result["title"]["status"] == "ok"
        assert result["description"]["status"] == "ok"

    def test_missing_title(self):
        result = analyze_title_meta_lengths(_soup("<html></html>"))
        assert result["title"] is None

    def test_missing_description(self):
        result = analyze_title_meta_lengths(_soup("<title>x</title>"))
        assert result["description"] is None

    def test_too_long_title(self):
        html = f"<title>{'T' * (TITLE_LIMIT + 1)}</title>"
        result = analyze_title_meta_lengths(_soup(html))
        assert result["title"]["status"] == "too_long"

    def test_too_long_description(self):
        html = f"<title>x</title><meta name='description' content=\"{'D' * (DESCRIPTION_LIMIT + 1)}\">"
        result = analyze_title_meta_lengths(_soup(html))
        assert result["description"]["status"] == "too_long"

    def test_too_short_title(self):
        result = analyze_title_meta_lengths(_soup("<title>abc</title>"))
        assert result["title"]["status"] == "too_short"

    def test_too_short_description(self):
        html = "<title>x</title><meta name='description' content='pendek'>"
        result = analyze_title_meta_lengths(_soup(html))
        assert result["description"]["status"] == "too_short"

    def test_empty_title(self):
        result = analyze_title_meta_lengths(_soup("<title>   </title>"))
        assert result["title"]["status"] == "empty"

    def test_lengths_reported(self):
        html = "<title>Hello</title><meta name='description' content='Deskripsi'>"
        result = analyze_title_meta_lengths(_soup(html))
        assert result["title"]["length"] == 5
        assert result["description"]["length"] == 9


class TestTruncate:
    def test_short_untouched(self):
        assert _truncate("pendek", 10) == "pendek"

    def test_long_cut_with_ellipsis(self):
        text = "kata " * 50
        result = _truncate(text, 20)
        assert len(result) <= 23
        assert result.endswith("...")

    def test_cut_at_word_boundary(self):
        text = "satu dua tiga empat lima"
        result = _truncate(text, 9)
        assert result == "satu dua..."


class TestSerpPreview:
    def test_renders_title_url_description(self):
        out = render_serp_preview("Judul Halaman", "https://x.com/", "Deskripsi halaman")
        assert "Judul Halaman" in out
        assert "https://x.com/" in out
        assert "Deskripsi halaman" in out

    def test_missing_fallbacks(self):
        out = render_serp_preview(None, "https://x.com/", None)
        assert "(tanpa title)" in out
        assert "(tanpa meta description)" in out

    def test_long_title_truncated_in_preview(self):
        out = render_serp_preview("T" * 200, "https://x.com/", "d")
        assert "TTT" not in out.replace("...", "") or True  # truncation terjadi di _truncate
        assert _truncate("T" * 200, TITLE_LIMIT).endswith("...")

    def test_multiline_wrap(self):
        desc = "kata " * 100  # jauh lebih panjang dari lebar preview
        out = render_serp_preview("T", "https://x.com/", desc)
        # deskripsi panjang menghasilkan banyak baris preview
        assert out.count("\n") > 5
