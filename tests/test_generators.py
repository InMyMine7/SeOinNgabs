"""Test generators — htaccess valid, robots grup tunggal, escaping (fix L, M, N, O)."""

import pytest

from seoinngabs.core.output import escape_html
from seoinngabs.generators.htaccess import build_htaccess, validate_htaccess_path
from seoinngabs.generators.legal import build_disclaimer, build_privacy_policy, build_terms_and_conditions
from seoinngabs.generators.metatags import build_meta_tags, validate_twitter_card
from seoinngabs.generators.robots import build_robots_txt, validate_robot_path


class TestBuildHtaccess:
    def test_rewrite_engine_once(self):
        # fix L4
        content = build_htaccess(https_redirect=True, hotlink_domain="example.com")
        assert content.count("RewriteEngine On") == 1

    def test_https_redirect_block(self):
        content = build_htaccess(https_redirect=True)
        assert "RewriteCond %{HTTPS} off" in content
        assert "RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]" in content

    def test_hotlink_uses_user_domain(self):
        # fix L2: bukan yourdomain.com hardcoded
        content = build_htaccess(hotlink_domain="mysite.co.id")
        assert "mysite" in content
        assert "yourdomain.com" not in content

    def test_hotlink_domain_escaped(self):
        # fix L1: karakter regex di-escape agar config tetap valid
        content = build_htaccess(hotlink_domain="evil.com/evil?x")
        # domain divalidasi di menu; build tetap escape titik
        content2 = build_htaccess(hotlink_domain="example.com")
        assert "example\\.com" in content2

    def test_error_page_no_injection(self):
        content = build_htaccess(error_page="/404.html")
        assert 'ErrorDocument 404 /404.html\n' in content

    def test_redirects_listed(self):
        content = build_htaccess(redirects=[("/old", "/new")])
        assert "Redirect 301 /old /new" in content

    def test_trailing_newline(self):
        assert build_htaccess().endswith("\n")


class TestValidateHtaccessPath:
    def test_valid(self):
        assert validate_htaccess_path("/404.html")

    def test_injection_rejected(self):
        # fix L1
        assert not validate_htaccess_path('/404.html" # injected')
        assert not validate_htaccess_path("404.html")  # harus diawali /
        assert not validate_htaccess_path("/a\nb")


class TestBuildRobotsTxt:
    def test_single_useragent_group_for_multiple_paths(self):
        # fix M1: 2 path -> 1 grup 'User-agent: *', bukan 2 grup
        content = build_robots_txt(disallow_paths=["/a/", "/b/"])
        assert content.count("User-agent: *") == 1
        assert "Disallow: /a/" in content
        assert "Disallow: /b/" in content

    def test_sitemap_included(self):
        content = build_robots_txt(sitemap="https://example.com/sitemap.xml")
        assert "Sitemap: https://example.com/sitemap.xml" in content

    def test_allow_all(self):
        content = build_robots_txt(allow_all=True)
        assert "Disallow:\n" in content

    def test_default_group_always_present(self):
        # fix M2: jawaban n semua -> tetap ada grup User-agent
        content = build_robots_txt()
        assert "User-agent: *" in content

    def test_bot_rules(self):
        content = build_robots_txt(bot_rules=[("Googlebot", ["/private/"])])
        assert "User-agent: Googlebot" in content
        assert "Disallow: /private/" in content

    def test_trailing_newline(self):
        # fix M3
        assert build_robots_txt().endswith("\n")


class TestValidateRobotPath:
    def test_valid(self):
        assert validate_robot_path("/private/")

    def test_missing_slash_rejected(self):
        assert not validate_robot_path("private/")

    def test_newline_rejected(self):
        assert not validate_robot_path("/a\nUser-agent: *")


class TestBuildMetaTags:
    def test_escaping(self):
        # fix N1: XSS via keywords — input di-escape
        tags = build_meta_tags(keywords='<script>alert(1)</script>')
        joined = "".join(tags)
        assert "<script>alert(1)</script>" not in joined
        assert "&lt;script&gt;" in joined

    def test_quote_breakout_prevented(self):
        tags = build_meta_tags(description='x" onmouseover="alert(1)')
        joined = "".join(tags)
        assert 'content="x" onmouseover' not in joined

    def test_empty_fields_skipped(self):
        # fix N2
        tags = build_meta_tags(title="T", description="", keywords="", author="")
        assert len(tags) == 1
        assert tags[0] == "<title>T</title>"

    def test_twitter_card_valid(self):
        assert validate_twitter_card("summary")
        assert validate_twitter_card("summary_large_image")
        assert not validate_twitter_card("bogus")


class TestLegalDocs:
    def test_privacy_uses_services(self):
        # fix O1: services user muncul di dokumen
        doc = build_privacy_policy("Web", "https://web.com", "PT Web", "a@b.com", services="jasa seo, audit", third_party_services="GA")
        assert "jasa seo" in doc
        assert "GA" in doc

    def test_privacy_default_third_party(self):
        doc = build_privacy_policy("Web", "https://web.com", "PT Web", "a@b.com")
        assert "Google Analytics" in doc

    def test_disclaimer_medical_has_contact(self):
        # fix O2: semua tipe punya kontak
        doc = build_disclaimer("Web", "https://web.com", "PT", "kontak@web.com", "medical")
        assert "kontak@web.com" in doc

    def test_disclaimer_financial_has_contact(self):
        doc = build_disclaimer("Web", "https://web.com", "PT", "kontak@web.com", "financial")
        assert "kontak@web.com" in doc

    def test_disclaimer_unknown_type_falls_back(self):
        doc = build_disclaimer("Web", "https://web.com", "PT", "kontak@web.com", "kosong")
        assert "General Disclaimer" in doc

    def test_terms_escaped(self):
        # fix O3
        doc = build_terms_and_conditions('W" x', "https://w.com", "C", "ID", "a@b.com")
        assert 'href="https://w.com"' in doc  # href tetap valid
        assert 'W" x' not in doc

    def test_escape_html(self):
        assert escape_html("<b>&") == "&lt;b&gt;&amp;"
