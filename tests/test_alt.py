"""Test analyzer.alt — Image alt checker (Tahap 4 fitur #2)."""

from bs4 import BeautifulSoup

from seoinngabs.analyzer.alt import alt_summary, analyze_image_alts

BASE = "https://example.com/page.html"


def _soup(html):
    return BeautifulSoup(html, "html.parser")


class TestAnalyzeImageAlts:
    def test_ok_alt(self):
        results = analyze_image_alts(_soup('<img src="a.png" alt="Logo situs">'), BASE)
        assert results[0]["status"] == "ok"
        assert results[0]["alt"] == "Logo situs"

    def test_missing_alt(self):
        results = analyze_image_alts(_soup('<img src="a.png">'), BASE)
        assert results[0]["status"] == "missing"
        assert results[0]["alt"] is None

    def test_empty_alt(self):
        # alt="" eksplisit = dekoratif, dibedakan dari missing
        results = analyze_image_alts(_soup('<img src="a.png" alt="">'), BASE)
        assert results[0]["status"] == "empty"

    def test_whitespace_alt_is_empty(self):
        results = analyze_image_alts(_soup('<img src="a.png" alt="   ">'), BASE)
        assert results[0]["status"] == "empty"

    def test_long_alt(self):
        long_alt = "x" * 126
        results = analyze_image_alts(_soup(f'<img src="a.png" alt="{long_alt}">'), BASE)
        assert results[0]["status"] == "long"

    def test_alt_at_limit_ok(self):
        alt = "x" * 125
        results = analyze_image_alts(_soup(f'<img src="a.png" alt="{alt}">'), BASE)
        assert results[0]["status"] == "ok"

    def test_lazy_image_checked(self):
        # gambar lazy (data-src tanpa src) tetap diperiksa
        results = analyze_image_alts(_soup('<img data-src="real.jpg" alt="Lazy">'), BASE)
        assert len(results) == 1
        assert results[0]["status"] == "ok"

    def test_dedup_same_url(self):
        html = '<img src="a.png" alt="x"><img src="a.png" alt="y">'
        results = analyze_image_alts(_soup(html), BASE)
        assert len(results) == 1

    def test_data_uri_ignored(self):
        results = analyze_image_alts(_soup('<img src="data:image/png;base64,AA" alt="x">'), BASE)
        assert results == []

    def test_relative_url_resolved(self):
        results = analyze_image_alts(_soup('<img src="img/a.png" alt="x">'), BASE)
        assert results[0]["url"] == "https://example.com/img/a.png"


class TestAltSummary:
    def test_counts(self):
        html = (
            '<img src="a.png" alt="ok1">'
            '<img src="b.png">'
            '<img src="c.png" alt="">'
            '<img src="d.png" alt="' + "x" * 130 + '">'
        )
        summary = alt_summary(analyze_image_alts(_soup(html), BASE))
        assert summary == {"ok": 1, "missing": 1, "empty": 1, "long": 1, "total": 4}

    def test_empty_page(self):
        assert alt_summary([]) == {"ok": 0, "missing": 0, "empty": 0, "long": 0, "total": 0}
