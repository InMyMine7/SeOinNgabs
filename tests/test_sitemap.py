"""Test generators.sitemap — sitemap generator & validator (Tahap 4 fitur #6)."""

from seoinngabs.generators.sitemap import build_sitemap, validate_sitemap


class TestBuildSitemap:
    def test_minimal_entry(self):
        xml = build_sitemap([{"loc": "https://x.com/"}])
        assert '<?xml version="1.0" encoding="UTF-8"?>' in xml
        assert "<urlset" in xml and "sitemaps.org" in xml
        assert "<loc>https://x.com/</loc>" in xml

    def test_full_entry(self):
        xml = build_sitemap([{
            "loc": "https://x.com/a",
            "lastmod": "2026-01-01",
            "changefreq": "daily",
            "priority": 0.8,
        }])
        assert "<lastmod>2026-01-01</lastmod>" in xml
        assert "<changefreq>daily</changefreq>" in xml
        assert "<priority>0.8</priority>" in xml

    def test_empty_loc_raises(self):
        import pytest
        with pytest.raises(ValueError):
            build_sitemap([{"loc": ""}])

    def test_too_many_urls_raises(self):
        import pytest
        with pytest.raises(ValueError):
            build_sitemap([{"loc": f"https://x.com/{i}"} for i in range(50001)])

    def test_xml_escaping(self):
        xml = build_sitemap([{"loc": "https://x.com/a&b"}])
        assert "&" in xml
        assert "<loc>https://x.com/a&b</loc>" not in xml

    def test_generated_sitemap_valid(self):
        # roundtrip: hasil build harus lolos validator
        xml = build_sitemap([{"loc": "https://x.com/", "lastmod": "2026-01-01"}])
        report = validate_sitemap(xml)
        assert report["valid"] is True
        assert report["url_count"] == 1


class TestValidateSitemap:
    def test_valid_sitemap(self):
        xml = build_sitemap([{"loc": "https://x.com/a"}, {"loc": "https://x.com/b"}])
        report = validate_sitemap(xml)
        assert report["valid"] is True
        assert report["url_count"] == 2
        assert report["errors"] == []

    def test_invalid_xml(self):
        report = validate_sitemap("not xml <<<")
        assert report["valid"] is False
        assert any("XML" in e for e in report["errors"])

    def test_missing_loc(self):
        xml = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc></loc></url>
</urlset>"""
        report = validate_sitemap(xml)
        assert report["valid"] is False
        assert any("<loc>" in e for e in report["errors"])

    def test_relative_loc_flagged(self):
        xml = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>/relative-path</loc></url>
</urlset>"""
        report = validate_sitemap(xml)
        assert report["valid"] is False
        assert any("absolut" in e for e in report["errors"])

    def test_bad_lastmod_warns(self):
        xml = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://x.com/</loc><lastmod>01-01-2026</lastmod></url>
</urlset>"""
        report = validate_sitemap(xml)
        assert report["valid"] is True
        assert any("lastmod" in w for w in report["warnings"])

    def test_good_lastmod_no_warning(self):
        xml = build_sitemap([{"loc": "https://x.com/", "lastmod": "2026-01-01"}])
        report = validate_sitemap(xml)
        assert report["warnings"] == []

    def test_priority_out_of_range_warns(self):
        xml = """<?xml version="1.0"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://x.com/</loc><priority>2.5</priority></url>
</urlset>"""
        report = validate_sitemap(xml)
        assert report["valid"] is True
        assert any("priority" in w for w in report["warnings"])

    def test_wrong_root_error(self):
        report = validate_sitemap("<html><body></body></html>")
        assert report["valid"] is False
        assert any("urlset" in e for e in report["errors"])
