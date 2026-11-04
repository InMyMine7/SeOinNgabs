"""Test analyzer.backlinks_gen & fetch — path data, domain, menu (fix C1-C5, D, P5)."""

import json
from pathlib import Path
from unittest.mock import patch

import responses

from seoinngabs.analyzer.backlinks_gen import check_backlink_url, load_backlink_sites
from seoinngabs.analyzer.fetch import fetch_page
from seoinngabs.core.url import is_valid_domain
from seoinngabs.data import BACKLINK_DB


class TestDataPath:
    def test_backlink_db_path_absolute(self):
        # fix C2: path absolut via package, bukan CWD
        assert BACKLINK_DB.is_absolute()
        assert BACKLINK_DB.exists()
        assert BACKLINK_DB.name == "backlink.json"

    def test_load_backlink_sites(self):
        sites = load_backlink_sites()
        assert len(sites) == 3000
        assert all(s.startswith("http") for s in sites)


class TestCheckBacklinkUrl:
    @responses.activate
    def test_ok(self):
        responses.add(responses.GET, "http://x.com/inmymine7", status=200)
        result = check_backlink_url("http://x.com/inmymine7")
        assert result["status"] == 200
        assert result["error"] is None

    @responses.activate
    def test_error_captured(self):
        result = check_backlink_url("https://nonexistent.invalid/x")
        assert result["status"] is None
        assert result["error"] is not None


class TestDomainValidation:
    def test_domain_with_path_rejected(self):
        # fix C4
        assert not is_valid_domain("example.com/x?a=1")

    def test_plain_domain_accepted(self):
        assert is_valid_domain("example.com")


class TestFetchPage:
    @responses.activate
    def test_scheme_normalization(self):
        # fix D2/J2: input tanpa scheme ditangani
        responses.add(responses.GET, "http://example.com/", body="ok")
        response = fetch_page("example.com")
        assert response.status_code == 200

    @responses.activate
    def test_head_fallback(self):
        # fix D4/H3
        responses.add(responses.HEAD, "http://example.com/", status=405)
        responses.add(responses.GET, "http://example.com/", status=200)
        from seoinngabs.analyzer.fetch import head_or_get
        assert head_or_get("http://example.com/").status_code == 200


class TestMenu:
    def test_menu_actions_complete(self):
        # fix P5: semua 17 fitur lama tetap ada di menu baru
        from seoinngabs.cli.menu import ACTIONS
        assert len(ACTIONS) == 17
        assert set(ACTIONS.keys()) == {str(i) for i in range(1, 18)}

    def test_menu_loop_exits_on_quit(self, capsys):
        from seoinngabs.cli.menu import run_menu
        with patch("builtins.input", side_effect=["q"]):
            run_menu()
        out = capsys.readouterr().out
        assert "17. Disclaimer Generator Tool" in out
