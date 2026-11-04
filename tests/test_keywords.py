"""Test research.keywords — URL encoding & parsing (fix B1-B4)."""

import responses

from seoinngabs.research.keywords import SUGGEST_URL, research_keyword

SUGGEST_XML = """<?xml version="1.0"?><toplevel>
<CompleteSuggestion><suggestion data="sepatu lari"/></CompleteSuggestion>
<CompleteSuggestion><suggestion data="sepatu &amp; sandal"/></CompleteSuggestion>
</toplevel>"""


class TestKeywordResearch:
    @responses.activate
    def test_url_encoding_ampersand(self):
        # fix B1: 'a&b' tidak lagi terpotong menjadi 'q=a'
        responses.add(responses.GET, SUGGEST_URL, body=SUGGEST_XML, status=200)
        research_keyword("a&b")
        url = responses.calls[0].request.url
        assert "q=a%26b" in url or "q=a%26b".replace("%26", "%26") in url

    @responses.activate
    def test_url_encoding_space(self):
        responses.add(responses.GET, SUGGEST_URL, body=SUGGEST_XML, status=200)
        research_keyword("sepatu lari")
        assert "q=sepatu+lari" in responses.calls[0].request.url

    @responses.activate
    def test_https_used(self):
        # fix B3
        responses.add(responses.GET, SUGGEST_URL, body=SUGGEST_XML, status=200)
        research_keyword("x")
        assert responses.calls[0].request.url.startswith("https://")

    @responses.activate
    def test_entity_decoded(self):
        # fix B4: &amp; ter-decode
        responses.add(responses.GET, SUGGEST_URL, body=SUGGEST_XML, status=200)
        assert "sepatu & sandal" in research_keyword("sepatu")

    @responses.activate
    def test_invalid_xml_returns_empty(self):
        responses.add(responses.GET, SUGGEST_URL, body="not xml", status=200)
        assert research_keyword("x") == []
