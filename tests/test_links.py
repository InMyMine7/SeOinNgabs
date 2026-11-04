"""Test analyzer.links — klasifikasi, urljoin, skip, nofollow, dedup (fix G1-G5)."""

from bs4 import BeautifulSoup

from seoinngabs.analyzer.links import classify_links

BASE = "https://www.example.com/page/"


def _soup(html):
    return BeautifulSoup(html, "html.parser")


class TestClassifyLinks:
    def test_apex_vs_www_is_internal(self):
        # fix G1
        result = classify_links(BASE, _soup('<a href="https://example.com/other">x</a>'))
        assert len(result["internal"]) == 1
        assert result["external"] == []

    def test_external_domain(self):
        result = classify_links(BASE, _soup('<a href="https://github.com/">x</a>'))
        assert len(result["external"]) == 1

    def test_relative_without_slash_resolved(self):
        # fix G2: 'page.html' tidak lagi hilang
        result = classify_links(BASE, _soup('<a href="page.html">x</a>'))
        assert result["internal"][0]["href"] == "https://www.example.com/page/page.html"

    def test_query_only_resolved(self):
        result = classify_links(BASE, _soup('<a href="?q=1">x</a>'))
        assert result["internal"][0]["href"] == "https://www.example.com/page/?q=1"

    def test_protocol_relative_resolved(self):
        result = classify_links(BASE, _soup('<a href="//cdn.other.com/x">x</a>'))
        assert result["external"][0]["href"] == "https://cdn.other.com/x"

    def test_root_relative(self):
        result = classify_links(BASE, _soup('<a href="/about">x</a>'))
        assert result["internal"][0]["href"] == "https://www.example.com/about"

    def test_skips_pseudo_protocols(self):
        # fix G3: mailto/tel/javascript skip eksplisit
        html = '<a href="mailto:a@b.com">m</a><a href="tel:+621">t</a><a href="javascript:void(0)">j</a><a href="#top">h</a>'
        result = classify_links(BASE, _soup(html))
        assert result["internal"] == []
        assert result["external"] == []
        assert set(result["skipped"]) == {"mailto:a@b.com", "tel:+621", "javascript:void(0)"}

    def test_nofollow_recorded(self):
        # fix G3: rel=nofollow
        html = '<a href="/x" rel="nofollow">x</a>'
        result = classify_links(BASE, _soup(html))
        assert result["internal"][0]["nofollow"] is True

    def test_nofollow_uppercase(self):
        html = '<a href="/x" rel="NoFollow">x</a>'
        result = classify_links(BASE, _soup(html))
        assert result["internal"][0]["nofollow"] is True

    def test_dedup_identical_links(self):
        # fix G5
        html = '<a href="/x">same</a><a href="/x">same</a>'
        result = classify_links(BASE, _soup(html))
        assert len(result["internal"]) == 1

    def test_anchor_text_captured(self):
        result = classify_links(BASE, _soup('<a href="/x">Klik <b>disini</b></a>'))
        assert result["internal"][0]["anchor"] == "Klik disini"

    def test_empty_href_ignored(self):
        result = classify_links(BASE, _soup('<a href="">x</a>'))
        assert result["internal"] == []
        assert result["external"] == []

    def test_include_subdomains_option(self):
        result = classify_links(BASE, _soup('<a href="https://blog.example.com/x">x</a>'), include_subdomains=True)
        assert len(result["internal"]) == 1
