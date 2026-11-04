"""Test analyzer.broken & redirects — urljoin, 301 terdeteksi, fallback GET (fix H1, H3, I1, I2)."""

import responses
from bs4 import BeautifulSoup

from seoinngabs.analyzer.broken import collect_links
from seoinngabs.analyzer.links import check_link_status


class TestCheckLinkStatus:
    @responses.activate
    def test_detects_301_without_following(self):
        # fix I1: 301 benar-benar terdeteksi
        responses.add(
            responses.HEAD, "https://example.com/old",
            status=301, headers={"Location": "https://example.com/new"},
        )
        result = check_link_status("https://example.com/old")
        assert result["status_code"] == 301
        assert result["redirected"] is True
        assert result["final_url"] == "https://example.com/new"

    @responses.activate
    def test_detects_302(self):
        responses.add(responses.HEAD, "https://example.com/x", status=302, headers={"Location": "https://example.com/y"})
        assert check_link_status("https://example.com/x")["status_code"] == 302

    @responses.activate
    def test_head_405_falls_back_to_get(self):
        # fix H3/D4: server menolak HEAD -> fallback GET
        responses.add(responses.HEAD, "https://example.com/x", status=405)
        responses.add(responses.GET, "https://example.com/x", status=200)
        result = check_link_status("https://example.com/x")
        assert result["status_code"] == 200

    @responses.activate
    def test_404_detected(self):
        responses.add(responses.HEAD, "https://example.com/missing", status=404)
        assert check_link_status("https://example.com/missing")["status_code"] == 404

    def test_request_error_captured_not_raised(self):
        # timeout/koneksi gagal -> error string, tidak crash
        result = check_link_status("https://nonexistent.invalid/x")
        assert result["status_code"] is None
        assert result["error"] is not None


class TestRelativeLinksNotBroken:
    """fix H1: link relatif tidak boleh MissingSchema -> broken palsu."""

    def test_urljoin_prevents_missing_schema(self):
        from seoinngabs.core.url import join_url
        base = "https://example.com/page/"
        assert join_url(base, "/about") == "https://example.com/about"
        # Jika di-resolve, check_link_status tidak menerima path relatif
        assert join_url(base, "page.html") == "https://example.com/page/page.html"


class TestCollectLinks:
    """Regresi: collect_links harus mengembalikan list of str (bukan crash)."""

    def test_returns_string_urls(self):
        # bug: sorted({*internal, *external}) melempar TypeError 'unhashable
        # type: dict' karena internal/external adalah list of dict
        soup = BeautifulSoup(
            '<a href="/x">a</a><a href="https://other.com/y">b</a><a href="/x">dup</a>',
            "html.parser",
        )
        links = collect_links("https://ngokang.my.id", soup)
        assert links == ["https://ngokang.my.id/x", "https://other.com/y"]
        assert all(isinstance(link, str) for link in links)

    def test_dedup_and_only_hrefs(self):
        soup = BeautifulSoup(
            '<a href="/a">a</a><a href="/a">b</a><a href="mailto:x@y.com">m</a>',
            "html.parser",
        )
        links = collect_links("https://site.com", soup)
        assert links == ["https://site.com/a"]
