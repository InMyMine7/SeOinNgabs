"""Test analyzer.density — script/style exclusion, n-gram, filter token (fix K1-K4)."""

from bs4 import BeautifulSoup

from seoinngabs.analyzer.density import count_ngrams, extract_text, tokenize


def _soup(html):
    return BeautifulSoup(html, "html.parser")


class TestExtractText:
    def test_script_style_excluded(self):
        # fix K1: strip eksplisit, tidak bergantung parser
        html = (
            "<html><head><style>styleword1 styleword2</style></head>"
            "<body><p>bodyword1</p><script>scriptword1 scriptword2</script></body></html>"
        )
        text = extract_text(_soup(html))
        assert "bodyword1" in text
        assert "scriptword1" not in text
        assert "styleword1" not in text

    def test_noscript_excluded(self):
        text = extract_text(_soup("<body><p>a</p><noscript>hiddenword</noscript></body>"))
        assert "hiddenword" not in text

    def test_body_text_preserved(self):
        text = extract_text(_soup("<body><h1>Halo</h1><p>dunia</p></body>"))
        assert "Halo" in text and "dunia" in text


class TestTokenize:
    def test_lowercase(self):
        assert tokenize("Halo DUNIA") == ["halo", "dunia"]

    def test_filters_single_char(self):
        # fix K3
        assert tokenize("a b seo") == ["seo"]

    def test_filters_pure_numbers(self):
        assert tokenize("2024 seo") == ["seo"]

    def test_unicode(self):
        assert "café" in tokenize("café")


class TestNgram:
    def test_unigram(self):
        assert count_ngrams(["sepatu", "lari", "sepatu"], "sepatu", 1) == 2

    def test_bigram(self):
        # fix K2: frasa didukung
        tokens = ["sepatu", "lari", "murah", "sepatu", "lari"]
        assert count_ngrams(tokens, "sepatu lari", 2) == 2

    def test_trigram(self):
        tokens = ["jual", "sepatu", "lari", "jual", "sepatu", "lari"]
        assert count_ngrams(tokens, "jual sepatu lari", 3) == 2

    def test_no_match(self):
        assert count_ngrams(["a", "b"], "b a", 2) == 0
