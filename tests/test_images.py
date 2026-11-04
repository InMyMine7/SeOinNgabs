"""Test analyzer.images — lazy-load, urljoin, ukuran nyata, full download (fix J1-J4)."""

import responses
from bs4 import BeautifulSoup

from seoinngabs.analyzer.images import collect_image_urls, measure_image, resolve_img_url

BASE = "https://example.com/page.html"


def _soup(html):
    return BeautifulSoup(html, "html.parser")


class TestResolveImgUrl:
    def test_plain_src(self):
        img = _soup('<img src="a.png">').img
        assert resolve_img_url(img, BASE) == "https://example.com/a.png"

    def test_data_src_lazy(self):
        # fix J3: lazy-load data-src
        img = _soup('<img src="placeholder.gif" data-src="real.jpg">').img
        assert resolve_img_url(img, BASE) == "https://example.com/page.html".replace("page.html", "real.jpg")

    def test_srcset_fallback(self):
        # fix J3: srcset -> kandidat pertama
        img = _soup('<img srcset="small.jpg 1x, big.jpg 2x">').img
        assert resolve_img_url(img, BASE) == "https://example.com/small.jpg"

    def test_protocol_relative(self):
        # fix J4
        img = _soup('<img src="//cdn.b.com/i.png">').img
        assert resolve_img_url(img, BASE) == "https://cdn.b.com/i.png"

    def test_data_uri_skipped(self):
        img = _soup('<img src="data:image/png;base64,AAA">').img
        assert resolve_img_url(img, BASE) is None

    def test_relative_path_correct(self):
        # fix J4: 'page.html' + 'img.png' -> /img.png (bukan /page.html/img.png)
        img = _soup('<img src="img.png">').img
        assert resolve_img_url(img, "https://x.com/dir/page.html") == "https://x.com/dir/img.png"


class TestCollectImageUrls:
    def test_dedup(self):
        soup = _soup('<img src="a.png"><img src="a.png"><img src="b.png">')
        assert len(collect_image_urls(soup, BASE)) == 2


class TestMeasureImage:
    @responses.activate
    def test_reads_full_body_size(self):
        # fix J1: isi diunduh -> ukuran nyata, bukan hanya header
        payload = b"x" * 5000
        responses.add(responses.GET, "https://example.com/i.png", body=payload, status=200)
        result = measure_image("https://example.com/i.png")
        assert result["size"] == 5000
        assert result["error"] is None
        assert result["load_time"] is not None

    @responses.activate
    def test_http_error_reported(self):
        responses.add(responses.GET, "https://example.com/missing.png", status=404)
        result = measure_image("https://example.com/missing.png")
        assert result["error"] is not None
        assert result["size"] == 0
