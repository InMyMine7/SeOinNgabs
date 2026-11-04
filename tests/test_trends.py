"""Test research.trends — endpoint RSS baru (fix A1-A4)."""

import responses

from seoinngabs.research import trends
from seoinngabs.research.trends import format_trends, get_trending_searches

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rss xmlns:ht="https://trends.google.com/trending/rss" version="2.0">
  <channel>
    <title>Daily Search Trends</title>
    <item><title>sepatu lari</title></item>
    <item><title>harga emas</title></item>
    <item><title>timnas indonesia</title></item>
  </channel>
</rss>"""


class TestTrends:
    @responses.activate
    def test_parses_rss_titles(self):
        # fix A1: tidak lagi memakai pytrends trending_searches (404)
        responses.add(responses.GET, "https://trends.google.com/trending/rss", body=SAMPLE_RSS, status=200)
        result = get_trending_searches()
        assert result == ["sepatu lari", "harga emas", "timnas indonesia"]

    @responses.activate
    def test_uses_geo_param(self):
        responses.add(responses.GET, "https://trends.google.com/trending/rss", body=SAMPLE_RSS, status=200)
        get_trending_searches(geo="US")
        assert "geo=US" in responses.calls[0].request.url

    @responses.activate
    def test_limit(self):
        responses.add(responses.GET, "https://trends.google.com/trending/rss", body=SAMPLE_RSS, status=200)
        assert len(get_trending_searches(limit=2)) == 2

    @responses.activate
    def test_ignores_empty_titles(self):
        rss = SAMPLE_RSS.replace("<title>harga emas</title>", "<title>  </title>")
        responses.add(responses.GET, "https://trends.google.com/trending/rss", body=rss, status=200)
        assert "harga emas" not in get_trending_searches()

    @responses.activate
    def test_invalid_xml_raises_value_error(self):
        responses.add(responses.GET, "https://trends.google.com/trending/rss", body="not xml <<<", status=200)
        try:
            get_trending_searches()
        except ValueError:
            return
        raise AssertionError("ValueError tidak dilempar untuk respons non-RSS")

    @responses.activate
    def test_http_error_raises(self):
        # fix A2: error terdeteksi (tidak traceback mentah di menu — ditangkap menu)
        responses.add(responses.GET, "https://trends.google.com/trending/rss", status=429)
        try:
            get_trending_searches()
        except Exception as e:
            assert "429" in str(e) or e.__class__.__name__ == "HTTPError"
            return
        raise AssertionError("Request gagal tidak melempar exception")

    def test_format_trends(self):
        output = format_trends(["a", "b"], geo="ID")
        assert "Indonesia" in output
        assert "1. a" in output
        assert "2. b" in output
