"""Test cli.args — mode argumen CLI (Tahap 4 fitur #9)."""

import pytest
import responses

from seoinngabs.cli.args import build_parser, run_cli


class TestParser:
    def test_all_commands_registered(self):
        parser = build_parser()
        # subcommand yang diharapkan
        expected = {"trends", "keywords", "status", "meta", "headings", "links", "broken",
                     "redirects", "trace", "images", "density", "og", "alt", "serp",
                     "crawl", "backlinks", "export", "security"}
        actual = set(parser._subparsers._group_actions[0].choices.keys())
        assert expected <= actual

    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit) as exc:
            build_parser().parse_args(["--version"])
        assert exc.value.code == 0

    def test_url_required_for_meta(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args(["meta"])

    def test_crawl_defaults(self):
        args = build_parser().parse_args(["crawl", "https://x.com/"])
        assert args.depth == 2
        assert args.max_pages == 20
        assert args.no_robots is False

    def test_export_options(self):
        args = build_parser().parse_args(["export", "u1", "u2", "--format", "json", "--output", "out"])
        assert args.urls == ["u1", "u2"]
        assert args.format == "json"
        assert args.output == "out"


class TestRunCli:
    def test_no_command_prints_help(self, capsys):
        assert run_cli([]) == 0
        out = capsys.readouterr().out
        assert "seoinngabs" in out.lower()

    @responses.activate
    def test_status_command(self, capsys):
        responses.add(responses.GET, "https://example.com/", status=200)
        assert run_cli(["status", "https://example.com/"]) == 0
        assert "200" in capsys.readouterr().out

    @responses.activate
    def test_status_command_with_redirect(self, capsys):
        responses.add(responses.GET, "http://example.com/a", status=301,
                      headers={"Location": "https://example.com/b"})
        responses.add(responses.GET, "https://example.com/b", status=200)
        assert run_cli(["status", "http://example.com/a"]) == 0
        out = capsys.readouterr().out
        assert "200" in out

    @responses.activate
    def test_meta_command(self, capsys):
        responses.add(responses.GET, "https://example.com/",
                       body="<title>T</title><meta name='description' content='D'>")
        assert run_cli(["meta", "https://example.com/"]) == 0
        out = capsys.readouterr().out
        assert "T" in out and "D" in out

    def test_error_returns_1(self, capsys):
        # URL invalid -> error ditangkap, exit code 1
        assert run_cli(["status", ""]) == 1

    @responses.activate
    def test_keywords_command(self, capsys):
        from seoinngabs.research.keywords import SUGGEST_URL

        responses.add(responses.GET, SUGGEST_URL,
                     body="<?xml version='1.0'?><toplevel><CompleteSuggestion>"
                          "<suggestion data='sepatu kets'/></CompleteSuggestion></toplevel>")
        assert run_cli(["keywords", "sepatu"]) == 0
        assert "sepatu kets" in capsys.readouterr().out

    @responses.activate
    def test_og_command(self, capsys):
        responses.add(responses.GET, "https://example.com/",
                      body='<meta property="og:title" content="X">')
        assert run_cli(["og", "https://example.com/"]) == 0
        assert "og:title" in capsys.readouterr().out

    @responses.activate
    def test_alt_command(self, capsys):
        responses.add(responses.GET, "https://example.com/", body='<img src="a.png" alt="A">')
        assert run_cli(["alt", "https://example.com/"]) == 0
        assert "OK" in capsys.readouterr().out

    @responses.activate
    def test_trace_command(self, capsys):
        responses.add(responses.GET, "https://example.com/old", status=301,
                      headers={"Location": "https://example.com/new"})
        responses.add(responses.GET, "https://example.com/new", status=200)
        assert run_cli(["trace", "https://example.com/old"]) == 0
        out = capsys.readouterr().out
        assert "301" in out and "loop: False" in out
