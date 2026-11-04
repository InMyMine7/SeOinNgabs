"""Test analyzer.redirect_tracer — redirect chain tracer (Tahap 4 fitur #4)."""

import responses

from seoinngabs.analyzer.redirect_tracer import trace_redirects


class TestTraceRedirects:
    @responses.activate
    def test_no_redirect_single_hop(self):
        responses.add(responses.GET, "https://example.com/", status=200)
        result = trace_redirects("https://example.com/")
        assert result["total_hops"] == 1
        assert result["loop"] is False
        assert result["completed"] is True
        assert result["final_url"] == "https://example.com/"
        assert result["hops"][0]["status"] == 200

    @responses.activate
    def test_single_301_chain(self):
        responses.add(responses.GET, "https://example.com/old", status=301, headers={"Location": "https://example.com/new"})
        responses.add(responses.GET, "https://example.com/new", status=200)
        result = trace_redirects("https://example.com/old")
        assert result["total_hops"] == 2
        assert result["hops"][0]["status"] == 301
        assert result["hops"][1]["status"] == 200
        assert result["final_url"] == "https://example.com/new"
        assert result["loop"] is False

    @responses.activate
    def test_multi_hop_chain(self):
        # a -> b -> c -> 200
        responses.add(responses.GET, "https://a.com/", status=301, headers={"Location": "https://b.com/"})
        responses.add(responses.GET, "https://b.com/", status=302, headers={"Location": "https://c.com/"})
        responses.add(responses.GET, "https://c.com/", status=200)
        result = trace_redirects("https://a.com/")
        assert result["total_hops"] == 3
        assert [h["status"] for h in result["hops"]] == [301, 302, 200]
        assert result["final_url"] == "https://c.com/"

    @responses.activate
    def test_loop_detected(self):
        # a -> b -> a (loop)
        responses.add(responses.GET, "https://a.com/", status=301, headers={"Location": "https://b.com/"})
        responses.add(responses.GET, "https://b.com/", status=301, headers={"Location": "https://a.com/"})
        result = trace_redirects("https://a.com/")
        assert result["loop"] is True
        assert result["completed"] is False

    @responses.activate
    def test_relative_location_resolved(self):
        # Location relatif di-resolve terhadap URL saat ini
        responses.add(responses.GET, "https://example.com/dir/page", status=302, headers={"Location": "../other"})
        responses.add(responses.GET, "https://example.com/other", status=200)
        result = trace_redirects("https://example.com/dir/page")
        assert result["final_url"] == "https://example.com/other"

    @responses.activate
    def test_max_hops_cut(self):
        # rantai 12 hop -> terpotong di 10
        for i in range(12):
            responses.add(responses.GET, f"https://x.com/{i}", status=301, headers={"Location": f"https://x.com/{i + 1}"})
        result = trace_redirects("https://x.com/0")
        assert result["completed"] is False
        assert result["loop"] is False
        assert result["total_hops"] == 10

    @responses.activate
    def test_error_recorded(self):
        result = trace_redirects("https://nonexistent.invalid/")
        assert result["completed"] is False
        assert result["hops"][0]["error"] is not None

    @responses.activate
    def test_redirect_without_location_stops(self):
        # status 301 tapi tanpa header Location -> berhenti (completed)
        responses.add(responses.GET, "https://example.com/x", status=301)
        result = trace_redirects("https://example.com/x")
        assert result["completed"] is True
        assert result["total_hops"] == 1

    @responses.activate
    def test_scheme_normalization(self):
        # input tanpa scheme tetap berfungsi
        responses.add(responses.GET, "http://example.com/", status=200)
        result = trace_redirects("example.com")
        assert result["completed"] is True
