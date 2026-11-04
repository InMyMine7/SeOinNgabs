"""Test export.exporters — CSV/JSON/HTML + batch (Tahap 4 fitur #8)."""

import csv
import io
import json
from pathlib import Path

import pytest
import responses

from seoinngabs.export.exporters import (
    batch_analyze,
    export_rows,
    rows_to_csv,
    rows_to_html,
    rows_to_json,
)

SAMPLE_ROWS = [
    {"url": "https://a.com/", "title": "Halaman A", "status": 200},
    {"url": "https://b.com/", "title": "B, dengan koma", "status": 200, "error": ""},
]


class TestRowsToCsv:
    def test_header_and_rows(self):
        out = rows_to_csv(SAMPLE_ROWS)
        reader = list(csv.DictReader(io.StringIO(out)))
        assert reader[0]["title"] == "Halaman A"
        assert reader[1]["title"] == "B, dengan koma"

    def test_union_columns(self):
        # kolom 'error' hanya ada di baris kedua tapi tetap jadi kolom
        out = rows_to_csv(SAMPLE_ROWS)
        assert "error" in out.splitlines()[0]

    def test_empty_rows(self):
        assert rows_to_csv([]) == ""

    def test_special_chars_quoted(self):
        rows = [{"a": 'kutip " dan\nbaris'}]
        out = rows_to_csv(rows)
        reader = list(csv.DictReader(io.StringIO(out)))
        assert reader[0]["a"] == 'kutip " dan\nbaris'


class TestRowsToJson:
    def test_roundtrip(self):
        out = rows_to_json(SAMPLE_ROWS)
        data = json.loads(out)
        assert data[0]["title"] == "Halaman A"

    def test_unicode_preserved(self):
        out = rows_to_json([{"nama": "Khôla Ünïcode"}])
        assert "Khôla Ünïcode" in out


class TestRowsToHtml:
    def test_table_rendered(self):
        out = rows_to_html(SAMPLE_ROWS, title="Uji")
        assert "<h1>Uji</h1>" in out
        assert "Halaman A" in out
        assert "<table" in out and "</table>" in out

    def test_escaping(self):
        out = rows_to_html([{"t": "<script>alert(1)</script>"}])
        assert "<script>alert(1)</script>" not in out.replace("<td>", "").replace("</td>", "")


class TestExportRows:
    def test_csv_file(self, tmp_path):
        path = export_rows(SAMPLE_ROWS, str(tmp_path / "l"), "csv")
        assert path.name == "l.csv"
        assert path.exists()
        assert "Halaman A" in path.read_text(encoding="utf-8")

    def test_json_file(self, tmp_path):
        path = export_rows(SAMPLE_ROWS, str(tmp_path / "l"), "json")
        assert path.suffix == ".json"
        assert json.loads(path.read_text(encoding="utf-8"))[0]["status"] == 200

    def test_html_file(self, tmp_path):
        path = export_rows(SAMPLE_ROWS, str(tmp_path / "l"), "html")
        assert path.suffix == ".html"

    def test_wrong_suffix_replaced(self, tmp_path):
        path = export_rows(SAMPLE_ROWS, str(tmp_path / "l.txt"), "csv")
        assert path.suffix == ".csv"

    def test_unknown_format_raises(self, tmp_path):
        with pytest.raises(ValueError):
            export_rows(SAMPLE_ROWS, str(tmp_path / "l"), "xlsx")

    def test_creates_parent_dirs(self, tmp_path):
        path = export_rows(SAMPLE_ROWS, str(tmp_path / "sub" / "dir" / "l"), "csv")
        assert path.exists()


class TestBatchAnalyze:
    @responses.activate
    def test_batch_success(self):
        responses.add(responses.GET, "https://a.com/", body="<title>A</title><meta name='description' content='d'>")
        responses.add(responses.GET, "https://b.com/", body="<title>B</title>")
        rows = batch_analyze(
            ["https://a.com/", "https://b.com/"],
            analyzer=lambda response, soup: {"title": soup.title.text},
            workers=2,
            progress=False,
        )
        titles = {r["title"] for r in rows}
        assert titles == {"A", "B"}
        assert all(r["error"] == "" for r in rows)

    @responses.activate
    def test_batch_error_captured(self):
        rows = batch_analyze(
            ["https://nonexistent.invalid/"],
            analyzer=lambda response, soup: {},
            workers=1,
            progress=False,
        )
        assert rows[0]["error"] != ""
        assert rows[0]["status"] == ""

    @responses.activate
    def test_batch_default_columns(self):
        responses.add(responses.GET, "https://a.com/", body="<html></html>")
        rows = batch_analyze(["https://a.com/"], analyzer=lambda r, s: {"x": 1}, workers=1, progress=False)
        assert rows[0]["url"] == "http://a.com/" or rows[0]["url"] == "https://a.com/"
        assert rows[0]["status"] == 200
