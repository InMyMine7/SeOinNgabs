"""Test analyzer.og — Open Graph / Twitter Card checker (Tahap 4 fitur #1)."""

from bs4 import BeautifulSoup

from seoinngabs.analyzer.og import analyze_og_twitter, og_twitter_recommendations


def _soup(html):
    return BeautifulSoup(html, "html.parser")


FULL = """
<meta property="og:title" content="Judul">
<meta property="og:type" content="website">
<meta property="og:image" content="https://x.com/i.png">
<meta property="og:url" content="https://x.com/">
<meta property="og:description" content="Desc">
<meta property="og:site_name" content="Site">
<meta property="og:locale" content="id_ID">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="T">
<meta name="twitter:description" content="D">
<meta name="twitter:image" content="https://x.com/i.png">
"""


class TestAnalyzeOgTwitter:
    def test_all_tags_found(self):
        tags = analyze_og_twitter(_soup(FULL))
        assert tags["og:title"] == "Judul"
        assert tags["og:type"] == "website"
        assert tags["twitter:card"] == "summary_large_image"

    def test_missing_when_absent(self):
        tags = analyze_og_twitter(_soup("<html></html>"))
        assert tags["og:title"] is None
        assert tags["twitter:card"] is None

    def test_empty_content_treated_missing(self):
        # content kosong = missing
        html = '<meta property="og:title" content="   ">'
        tags = analyze_og_twitter(_soup(html))
        assert tags["og:title"] is None

    def test_case_insensitive_attribute(self):
        # NAME="Twitter:Card" huruf besar tetap terbaca
        html = '<meta NAME="twitter:card" CONTENT="summary">'
        tags = analyze_og_twitter(_soup(html))
        assert tags["twitter:card"] == "summary"

    def test_og_via_name_attribute_fallback(self):
        # og:* ditulis via name= (non-standar tapi umum) — fallback tetap terbaca
        html = '<meta name="og:title" content="Via Name">'
        tags = analyze_og_twitter(_soup(html))
        assert tags["og:title"] == "Via Name"


class TestRecommendations:
    def test_no_recommendation_when_complete(self):
        tags = analyze_og_twitter(_soup(FULL))
        assert og_twitter_recommendations(tags) == []

    def test_missing_required_og_listed(self):
        tags = analyze_og_twitter(_soup("<html></html>"))
        recs = og_twitter_recommendations(tags)
        assert any("og:title" in r for r in recs)
        assert any("og:image" in r for r in recs)
        assert any("og:url" in r for r in recs)
        assert any("og:type" in r for r in recs)

    def test_missing_twitter_card_listed(self):
        tags = analyze_og_twitter(_soup("<html></html>"))
        recs = og_twitter_recommendations(tags)
        assert any("twitter:card" in r for r in recs)

    def test_invalid_twitter_card_type_flagged(self):
        html = '<meta name="twitter:card" content="bogus">'
        recs = og_twitter_recommendations(analyze_og_twitter(_soup(html)))
        assert any("tidak valid" in r for r in recs)

    def test_valid_twitter_card_not_flagged(self):
        html = '<meta name="twitter:card" content="summary">'
        recs = og_twitter_recommendations(analyze_og_twitter(_soup(html)))
        assert not any("tidak valid" in r for r in recs)
