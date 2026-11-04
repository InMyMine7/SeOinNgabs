"""Test analyzer.meta — case-insensitive attrs, KeyError, canonical relatif (fix E1-E6)."""

import responses

from seoinngabs.analyzer.meta import extract_page_meta

PAGE = """<html><head>
<title>  </title>
<META NAME="Description" CONTENT="deskripsi besar">
<link REL="Canonical" HREF="/relative-path">
</head><body></body></html>"""


class TestExtractPageMeta:
    @responses.activate
    def test_meta_name_case_insensitive(self):
        # fix E2: NAME="Description" harus terbaca
        responses.add(responses.GET, "http://example.com/", body=PAGE)
        meta = extract_page_meta("http://example.com/")
        assert meta["meta_description"] == "deskripsi besar"

    @responses.activate
    def test_canonical_case_insensitive_and_resolved(self):
        # fix E2 + E3: REL="Canonical" + href relatif -> absolute
        responses.add(responses.GET, "http://example.com/", body=PAGE)
        meta = extract_page_meta("http://example.com/")
        assert meta["canonical"] == "http://example.com/relative-path"

    @responses.activate
    def test_whitespace_title_is_none(self):
        # fix E4: <title>  </title> = kosong
        responses.add(responses.GET, "http://example.com/", body=PAGE)
        meta = extract_page_meta("http://example.com/")
        assert meta["title"] is None

    @responses.activate
    def test_missing_tags_no_crash(self):
        # fix E1: meta/link tanpa content/href tidak boleh KeyError
        page = "<html><head><meta name='description'><link rel='canonical'></head></html>"
        responses.add(responses.GET, "http://example.com/", body=page)
        meta = extract_page_meta("http://example.com/")
        assert meta["meta_description"] is None
        assert meta["canonical"] is None

    @responses.activate
    def test_non_200_still_analyzed(self):
        # fix E5: status 206 tetap dianalisis
        responses.add(responses.GET, "http://example.com/", body=PAGE, status=206)
        meta = extract_page_meta("http://example.com/")
        assert meta["status"] == 206
        assert meta["meta_description"] == "deskripsi besar"

    @responses.activate
    def test_og_image_list_content(self):
        # fix E1: property bisa berupa list (multi-valued) — tidak boleh crash
        page = '<meta property="og:image" content="img.png">'
        responses.add(responses.GET, "http://example.com/", body=page)
        meta = extract_page_meta("http://example.com/")
        assert meta["og_image"] == "img.png"

    @responses.activate
    def test_multi_rel_canonical(self):
        # rel="alternate canonical" (list) tetap dikenali
        page = '<link rel="alternate canonical" href="https://x.com/c">'
        responses.add(responses.GET, "http://example.com/", body=page)
        meta = extract_page_meta("http://example.com/")
        assert meta["canonical"] == "https://x.com/c"
