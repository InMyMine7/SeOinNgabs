"""Test core.url — normalisasi scheme, validasi domain, same_site (fix D2, C4, G1)."""

import pytest

from seoinngabs.core.errors import InvalidURLError
from seoinngabs.core.url import is_valid_domain, join_url, normalize_url, same_site


class TestNormalizeUrl:
    def test_adds_scheme_when_missing(self):
        assert normalize_url("example.com") == "http://example.com"

    def test_preserves_https(self):
        assert normalize_url("https://example.com") == "https://example.com"

    def test_lowercase_scheme_uppercase_input(self):
        # fix D2: 'HTTPS://EXAMPLE.COM' tidak lagi jadi 'http://HTTPS://EXAMPLE.COM'
        assert normalize_url("HTTPS://EXAMPLE.COM") == "https://EXAMPLE.COM"

    def test_empty_raises(self):
        with pytest.raises(InvalidURLError):
            normalize_url("")

    def test_whitespace_only_raises(self):
        with pytest.raises(InvalidURLError):
            normalize_url("   ")

    def test_preserves_path_and_query(self):
        assert normalize_url("example.com/path?q=1") == "http://example.com/path?q=1"


class TestIsValidDomain:
    def test_valid(self):
        assert is_valid_domain("example.com")

    def test_valid_subdomain(self):
        assert is_valid_domain("blog.example.co.id")

    def test_rejects_with_path(self):
        # fix C4: 'example.com/x?a=1' ditolak
        assert not is_valid_domain("example.com/x?a=1")

    def test_rejects_empty(self):
        assert not is_valid_domain("")

    def test_rejects_double_dot(self):
        assert not is_valid_domain("exa..mple.com")

    def test_rejects_injection(self):
        assert not is_valid_domain("example.com\nGET / HTTP/1.1")


class TestJoinUrl:
    def test_relative(self):
        assert join_url("https://a.com/dir/page.html", "img.png") == "https://a.com/dir/img.png"

    def test_root_relative(self):
        assert join_url("https://a.com/dir/page.html", "/about") == "https://a.com/about"

    def test_protocol_relative(self):
        # fix J4: '//cdn' tidak lagi jadi 'https://a.com//cdn'
        assert join_url("https://a.com/page.html", "//cdn.b.com/i.png") == "https://cdn.b.com/i.png"

    def test_query_only(self):
        assert join_url("https://a.com/dir/page.html", "?q=1") == "https://a.com/dir/page.html?q=1"

    def test_absolute_untouched(self):
        assert join_url("https://a.com/", "https://b.com/x") == "https://b.com/x"


class TestSameSite:
    def test_www_vs_apex_same(self):
        # fix G1: www dan apex adalah satu situs
        assert same_site("https://www.example.com/page/", "https://example.com/other")

    def test_different_domain_not_same(self):
        assert not same_site("https://www.example.com/", "https://other.com/")

    def test_subdomain_not_same_by_default(self):
        assert not same_site("https://example.com/", "https://sub.example.com/x")

    def test_subdomain_same_when_included(self):
        assert same_site("https://example.com/", "https://sub.example.com/x", include_subdomains=True)

    def test_case_insensitive_host(self):
        assert same_site("https://EXAMPLE.com/", "https://example.COM/x")
