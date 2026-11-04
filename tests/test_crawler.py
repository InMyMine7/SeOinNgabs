"""Test crawler + robots parser (Tahap 4 fitur #5)."""

import responses

from seoinngabs.analyzer.crawler import crawl_site
from seoinngabs.analyzer.robots_parser import fetch_robots_txt, parse_robots_txt


class TestParseRobotsTxt:
    def test_disallow_all(self):
        robots = parse_robots_txt("User-agent: *\nDisallow: /")
        assert not robots.is_allowed("/apa-pun")

    def test_allow_all(self):
        robots = parse_robots_txt("User-agent: *\nDisallow:")
        assert robots.is_allowed("/apa-pun")

    def test_specific_path_disallowed(self):
        robots = parse_robots_txt("User-agent: *\nDisallow: /private/")
        assert not robots.is_allowed("/private/secret")
        assert robots.is_allowed("/public/page")

    def test_allow_overrides_disallow(self):
        # longest match menang: Allow /private/ok lebih panjang dari Disallow /private/
        robots = parse_robots_txt("User-agent: *\nDisallow: /private/\nAllow: /private/ok")
        assert robots.is_allowed("/private/ok")
        assert not robots.is_allowed("/private/bad")

    def test_specific_agent_over_wildcard(self):
        robots = parse_robots_txt("User-agent: *\nDisallow: /\nUser-agent: SeOinNgabsBot\nDisallow:")
        assert robots.is_allowed("/x", user_agent="SeOinNgabsBot")
        assert not robots.is_allowed("/x", user_agent="LainBot")

    def test_crawl_delay_parsed(self):
        robots = parse_robots_txt("User-agent: *\nCrawl-delay: 5")
        assert robots.get_crawl_delay() == 5.0

    def test_crawl_delay_missing(self):
        robots = parse_robots_txt("User-agent: *\nDisallow:")
        assert robots.get_crawl_delay() is None

    def test_sitemap_collected(self):
        robots = parse_robots_txt("Sitemap: https://x.com/sitemap.xml")
        assert "https://x.com/sitemap.xml" in robots.sitemaps

    def test_comments_and_blank_ignored(self):
        robots = parse_robots_txt("# komentar\n\nUser-agent: *\nDisallow: /a # trailing\n")
        assert not robots.is_allowed("/a")

    def test_empty_content_allows_all(self):
        robots = parse_robots_txt("")
        assert robots.is_allowed("/x")


class TestFetchRobotsTxt:
    @responses.activate
    def test_fetch_and_parse(self):
        responses.add(responses.GET, "https://example.com/robots.txt", body="User-agent: *\nDisallow: /admin/")
        robots = fetch_robots_txt("https://example.com/")
        assert not robots.is_allowed("/admin/x")

    @responses.activate
    def test_missing_robots_allows_all(self):
        responses.add(responses.GET, "https://example.com/robots.txt", status=404)
        robots = fetch_robots_txt("https://example.com/")
        assert robots.is_allowed("/x")


class TestCrawlSite:
    @responses.activate
    def test_crawl_single_page(self):
        responses.add(responses.GET, "https://example.com/", body="<html><a href='/about'>x</a></html>",
                      headers={"Content-Type": "text/html"})
        results = crawl_site("https://example.com/", max_depth=0, max_pages=5, respect_robots=False, delay=0)
        assert len(results) == 1
        assert results[0]["status"] == 200
        assert results[0]["depth"] == 0

    @responses.activate
    def test_crawl_follows_internal_links(self):
        responses.add(responses.GET, "https://example.com/",
                      body="<html><a href='/a'>A</a><a href='/b'>B</a></html>",
                      headers={"Content-Type": "text/html"})
        responses.add(responses.GET, "https://example.com/a", body="<html></html>",
                      headers={"Content-Type": "text/html"})
        responses.add(responses.GET, "https://example.com/b", body="<html></html>",
                      headers={"Content-Type": "text/html"})
        results = crawl_site("https://example.com/", max_depth=1, max_pages=10, respect_robots=False, delay=0)
        urls = {r["url"] for r in results}
        assert "https://example.com/a" in urls
        assert "https://example.com/b" in urls

    @responses.activate
    def test_page_limit_respected(self):
        responses.add(responses.GET, "https://example.com/",
                      body="<html><a href='/a'>A</a><a href='/b'>B</a><a href='/c'>C</a></html>",
                      headers={"Content-Type": "text/html"})
        for p in ["a", "b", "c"]:
            responses.add(responses.GET, f"https://example.com/{p}", body="<html></html>",
                          headers={"Content-Type": "text/html"})
        results = crawl_site("https://example.com/", max_depth=1, max_pages=2, respect_robots=False, delay=0)
        assert len(results) <= 2

    @responses.activate
    def test_external_links_not_crawled(self):
        responses.add(responses.GET, "https://example.com/",
                      body="<html><a href='https://other.com/x'>ext</a></html>",
                      headers={"Content-Type": "text/html"})
        results = crawl_site("https://example.com/", max_depth=2, max_pages=10, respect_robots=False, delay=0)
        assert len(results) == 1

    @responses.activate
    def test_robots_disallow_respected(self):
        responses.add(responses.GET, "https://example.com/robots.txt", body="User-agent: *\nDisallow: /")
        responses.add(responses.GET, "https://example.com/", body="<html></html>",
                      headers={"Content-Type": "text/html"})
        results = crawl_site("https://example.com/", max_depth=1, max_pages=5, respect_robots=True, delay=0)
        assert results[0]["status"] == "robots-disallow"

    @responses.activate
    def test_non_html_skipped(self):
        responses.add(responses.GET, "https://example.com/", body="binary",
                      headers={"Content-Type": "application/pdf"})
        results = crawl_site("https://example.com/", max_depth=1, max_pages=5, respect_robots=False, delay=0)
        assert results[0]["status"] != 200 or results[0]["links"] == 0

    @responses.activate
    def test_fragment_and_duplicates_removed(self):
        responses.add(responses.GET, "https://example.com/",
                      body="<html><a href='/a#sec'>A</a><a href='/a'>A</a></html>",
                      headers={"Content-Type": "text/html"})
        responses.add(responses.GET, "https://example.com/a", body="<html></html>",
                      headers={"Content-Type": "text/html"})
        results = crawl_site("https://example.com/", max_depth=1, max_pages=10, respect_robots=False, delay=0)
        a_count = sum(1 for r in results if r["url"] == "https://example.com/a")
        assert a_count == 1
