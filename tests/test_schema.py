"""Test generators.schema — JSON-LD generator (Tahap 4 fitur #7)."""

import json

import pytest

from seoinngabs.generators.schema import (
    build_article_schema,
    build_breadcrumb_schema,
    build_local_business_schema,
    build_organization_schema,
    build_website_schema,
    render_json_ld,
)


class TestWebsiteSchema:
    def test_basic(self):
        s = build_website_schema("Situs", "https://x.com")
        assert s["@type"] == "WebSite"
        assert s["@context"] == "https://schema.org"
        assert s["name"] == "Situs"
        assert "potentialAction" not in s

    def test_with_search_action(self):
        s = build_website_schema("S", "https://x.com", search_url="https://x.com/?s={search_term_string}")
        assert s["potentialAction"]["@type"] == "SearchAction"
        assert s["potentialAction"]["target"]["urlTemplate"] == "https://x.com/?s={search_term_string}"
        assert s["potentialAction"]["query-input"] == "required name=search_term_string"

    def test_description(self):
        s = build_website_schema("S", "https://x.com", description="Situs keren")
        assert s["description"] == "Situs keren"


class TestOrganizationSchema:
    def test_basic(self):
        s = build_organization_schema("Org", "https://x.com")
        assert s["@type"] == "Organization"
        assert "logo" not in s
        assert "sameAs" not in s

    def test_with_logo_and_socials(self):
        s = build_organization_schema("Org", "https://x.com", logo="https://x.com/l.png",
                                      same_as=["https://fb.com/x", "https://x.com/x"])
        assert s["logo"] == "https://x.com/l.png"
        assert len(s["sameAs"]) == 2


class TestArticleSchema:
    def test_full(self):
        s = build_article_schema("Judul", "https://x.com/a", image="i.png", author="Ani",
                                 date_published="2026-01-01", publisher="X Media")
        assert s["@type"] == "Article"
        assert s["author"] == {"@type": "Person", "name": "Ani"}
        assert s["publisher"]["@type"] == "Organization"
        assert s["datePublished"] == "2026-01-01"

    def test_minimal(self):
        s = build_article_schema("J", "https://x.com/a")
        assert "author" not in s
        assert "publisher" not in s


class TestLocalBusinessSchema:
    def test_address(self):
        s = build_local_business_schema("Warung", "https://w.com", "Jl. Mawar 1", "Bandung",
                                        "Jawa Barat", "40111", "022-123", "img.png")
        addr = s["address"]
        assert addr["@type"] == "PostalAddress"
        assert addr["streetAddress"] == "Jl. Mawar 1"
        assert addr["addressLocality"] == "Bandung"
        assert addr["addressRegion"] == "Jawa Barat"
        assert addr["postalCode"] == "40111"
        assert s["telephone"] == "022-123"


class TestBreadcrumbSchema:
    def test_positions(self):
        crumbs = [{"name": "Home", "url": "https://x.com/"}, {"name": "A", "url": "https://x.com/a"}]
        s = build_breadcrumb_schema(crumbs)
        assert s["@type"] == "BreadcrumbList"
        items = s["itemListElement"]
        assert [i["position"] for i in items] == [1, 2]
        assert items[0]["name"] == "Home"

    def test_missing_name_raises(self):
        with pytest.raises(ValueError):
            build_breadcrumb_schema([{"name": "", "url": "https://x.com/"}])

    def test_missing_url_raises(self):
        with pytest.raises(ValueError):
            build_breadcrumb_schema([{"name": "A", "url": ""}])


class TestRenderJsonLd:
    def test_valid_json_output(self):
        s = build_website_schema("S", "https://x.com")
        block = render_json_ld(s)
        assert block.startswith('<script type="application/ld+json">')
        assert block.endswith("</script>")
        payload = block[block.index("\n") + 1:block.rindex("</script>")].strip()
        assert json.loads(payload) == s

    def test_unicode_preserved(self):
        s = build_website_schema("Situs Khôla", "https://x.com")
        assert "Khôla" in render_json_ld(s)
