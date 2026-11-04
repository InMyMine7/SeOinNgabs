"""Test analyzer.security — HTTPS/SSL & security headers (Tahap 4 fitur #10)."""

import responses

from seoinngabs.analyzer.security import SECURITY_HEADERS, check_security


class TestCheckSecurity:
    @responses.activate
    def test_https_and_headers(self):
        # halaman https dengan semua header aman
        responses.add(responses.GET, "http://example.com/", status=301,
                      headers={"Location": "https://example.com/"})
        responses.add(
            responses.GET, "https://example.com/", status=200,
            headers={name: "dummy" for name in SECURITY_HEADERS},
        )
        report = check_security("https://example.com/")
        assert report["https"] is True
        assert report["http_redirects_https"] is True
        assert report["missing_headers"] == []

    @responses.activate
    def test_http_only_no_ssl(self):
        responses.add(responses.GET, "http://example.com/", status=200)
        responses.add(responses.GET, "https://example.com/", status=200)
        report = check_security("http://example.com/")
        assert report["https"] is False
        assert report["http_redirects_https"] is False
        # HSTS tidak diwajibkan untuk situs non-HTTPS
        assert not any("Strict-Transport-Security — wajib" in m for m in report["missing_headers"])

    @responses.activate
    def test_missing_headers_reported(self):
        responses.add(responses.GET, "http://example.com/", status=301,
                      headers={"Location": "https://example.com/"})
        responses.add(responses.GET, "https://example.com/", status=200)  # tanpa header
        report = check_security("https://example.com/")
        names = " ".join(report["missing_headers"])
        assert "Content-Security-Policy" in names
        assert "X-Content-Type-Options" in names
        assert "Strict-Transport-Security" in names

    @responses.activate
    def test_csp_frame_ancestors_replaces_xfo(self):
        # X-Frame-Options hilang tapi CSP punya frame-ancestors -> tidak missing
        responses.add(responses.GET, "http://example.com/", status=301,
                      headers={"Location": "https://example.com/"})
        headers = {n: "x" for n in SECURITY_HEADERS if n != "X-Frame-Options"}
        headers["Content-Security-Policy"] = "frame-ancestors 'none'"
        responses.add(responses.GET, "https://example.com/", status=200, headers=headers)
        report = check_security("https://example.com/")
        assert not any("X-Frame-Options" in m for m in report["missing_headers"])

    @responses.activate
    def test_https_url_scheme_detection(self):
        responses.add(responses.GET, "https://example.com/", status=200)
        report = check_security("https://example.com/")
        assert report["https"] is True
