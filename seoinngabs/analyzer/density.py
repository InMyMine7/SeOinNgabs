"""Keyword density checker."""

import re
from typing import List

from bs4 import BeautifulSoup

from .fetch import fetch_page, parse_soup

STRIP_TAGS = ("script", "style", "noscript", "template")
WORD_RE = re.compile(r"\w+", re.UNICODE)
MIN_TOKEN_LEN = 2


def extract_text(soup) -> str:
    """Page text without script/style/noscript/template."""
    for tag_name in STRIP_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    return soup.get_text(" ", strip=True)


def tokenize(text: str) -> List[str]:
    """Case-folded tokens, short/pure-number tokens filtered."""
    return [
        w for w in WORD_RE.findall(text.lower())
        if len(w) >= MIN_TOKEN_LEN and not w.isdigit()
    ]


def count_ngrams(tokens: List[str], keyword: str, n: int) -> int:
    """Count occurrences of an n-gram keyword in the token list."""
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
    """Interactive: compute keyword density (single word or phrase)."""
    from ..core.ui import ask, ask_url, fail, header, label_value, success, warn

    print(header("Keyword Density Checker", "Word or phrase density (1-3 gram)"))
    url = ask_url()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return

    keyword = ask("Keyword or phrase (e.g. \"seo tools\")").strip().lower()
    if not keyword:
        print(fail("Keyword cannot be empty."))
        return

    tokens = tokenize(extract_text(soup))
    total_words = len(tokens)
    if total_words == 0:
        print(warn("This page contains no text."))
        return

    n = len(keyword.split())
    if n > 3:
        print(warn("Only 1-3 word phrases are supported; extra words ignored."))
        n = 3
    frequency = count_ngrams(tokens, " ".join(keyword.split()[:3]), n)
    density = frequency / total_words * 100
    print()
    print(label_value("Keyword", f"'{keyword}'"))
    print(label_value("Occurrences", f"{frequency} of {total_words} words"))
    print(label_value("Density", f"{density:.2f}%"))
    if density > 5:
        print(warn("Density above 5% may look like keyword stuffing."))
    elif density < 0.5 and frequency == 0:
        print(warn("Keyword not found on this page."))
    else:
        print(success("Density within a reasonable range."))
