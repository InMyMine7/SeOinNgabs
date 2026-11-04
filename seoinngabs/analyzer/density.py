"""Keyword density checker (fix K1-K5).

Perbaikan vs main.py lama:
- script/style/noscript/template di-strip EKSPLISIT sebelum get_text (fix K1
  — tidak lagi bergantung perilaku parser).
- Dukung frasa (bigram/trigram via n-gram) + kata tunggal (fix K2).
- Token 1-huruf dan angka murni difilter (fix K3).
- Session terpusat: timeout/UA (fix K4).
"""

import re
from collections import Counter
from typing import List

from bs4 import BeautifulSoup

from ..core.output import colorize
from .fetch import fetch_page, parse_soup

STRIP_TAGS = ("script", "style", "noscript", "template")
WORD_RE = re.compile(r"\w+", re.UNICODE)
MIN_TOKEN_LEN = 2


def extract_text(soup) -> str:
    """Teks halaman tanpa script/style/noscript/template (fix K1)."""
    for tag_name in STRIP_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    return soup.get_text(" ", strip=True)


def tokenize(text: str) -> List[str]:
    """Tokenisasi case-folded, filter token pendek/angka (fix K3)."""
    return [
        w for w in WORD_RE.findall(text.lower())
        if len(w) >= MIN_TOKEN_LEN and not w.isdigit()
    ]


def count_ngrams(tokens: List[str], keyword: str, n: int) -> int:
    """Hitung kemunculan n-gram keyword dalam token list (fix K2)."""
    if n < 1:
        return 0
    target = keyword.lower().split()
    if len(target) != n:
        return 0
    count = 0
    for i in range(len(tokens) - n + 1):
        if tokens[i:i + n] == target:
            count += 1
    return count


def check_keyword_density() -> None:
    """Menu interaktif: hitung kepadatan kata kunci (mendukung frasa)."""
    print("=====Keyword Density Checker=====")
    url = input("\nMasukkan URL halaman: ").strip()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print("Terjadi kesalahan permintaan:", e)
        return

    keyword = input("Masukkan kata kunci yang ingin diperiksa (kata atau frasa): ").strip().lower()
    if not keyword:
        print(colorize("Kata kunci tidak dimasukkan.", "red"))
        return

    tokens = tokenize(extract_text(soup))
    total_words = len(tokens)

    if total_words == 0:
        print(colorize("Halaman tidak mengandung teks.", "red"))
        return

    n = len(keyword.split())
    frequency = count_ngrams(tokens, keyword, n)
    density = frequency / total_words * 100
    unit = "frasa" if n > 1 else "kata"
    print(
        colorize(
            f"Kepadatan kata kunci '{keyword}': {density:.2f}% ({frequency} kali dari {total_words} kata) "
            f"[dihitung sebagai {unit} {n}-gram]",
            "green",
        )
    )
