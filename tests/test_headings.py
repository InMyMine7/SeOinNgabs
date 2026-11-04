"""Test analyzer.headings — h1 ganda, lompatan, kosong (fix F1-F4)."""

from bs4 import BeautifulSoup

from seoinngabs.analyzer.headings import analyze_headings


def _soup(html):
    return BeautifulSoup(html, "html.parser")


class TestAnalyzeHeadings:
    def test_multiple_h1_detected(self):
        result = analyze_headings(_soup("<h1>A</h1><h1>B</h1>"))
        assert result["h1_count"] == 2

    def test_single_h1_ok(self):
        result = analyze_headings(_soup("<h1>A</h1><h2>b</h2>"))
        assert result["h1_count"] == 1
        assert not result["skipped_levels"]

    def test_no_h1_detected(self):
        result = analyze_headings(_soup("<h2>a</h2>"))
        assert result["h1_count"] == 0

    def test_level_jump_detected(self):
        # fix F2: h1 -> h3 dilaporkan
        result = analyze_headings(_soup("<h1>a</h1><h3>jump</h3>"))
        assert len(result["skipped_levels"]) == 1
        assert "h1 -> h3" in result["skipped_levels"][0]

    def test_no_false_jump_from_h2_to_h3(self):
        result = analyze_headings(_soup("<h1>a</h1><h2>b</h2><h3>c</h3>"))
        assert result["skipped_levels"] == []

    def test_empty_heading_recorded(self):
        # fix F1: heading kosong dicatat
        result = analyze_headings(_soup("<h1>a</h1><h2>   </h2>"))
        assert "h2" in result["empty_headings"]

    def test_backward_jump_not_flagged(self):
        # h3 -> h2 (mundur) bukan lompatan maju
        result = analyze_headings(_soup("<h1>a</h1><h3>b</h3><h2>c</h2>"))
        # h1->h3 tetap satu lompatan; h3->h2 tidak ditambah
        assert len(result["skipped_levels"]) == 1
