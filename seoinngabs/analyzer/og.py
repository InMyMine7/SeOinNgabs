"""Open Graph / Twitter Card checker (Tahap 4 fitur #1).

Memeriksa kelengkapan tag Open Graph (og:) dan Twitter Card (twitter:)
berdasarkan praktik umum:
- OG wajib: og:title, og:type, og:image, og:url
- OG opsional: og:description, og:site_name, og:locale
- Twitter wajib: twitter:card
- Twitter opsional: twitter:title, twitter:description, twitter:image

Nilai kosong dianggap missing. Hasil: dict {tag: value|None} + rekomendasi.
"""

from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from ..core.output import colorize
from .fetch import fetch_page, parse_soup

OG_REQUIRED = ["og:title", "og:type", "og:image", "og:url"]
OG_OPTIONAL = ["og:description", "og:site_name", "og:locale"]
TWITTER_REQUIRED = ["twitter:card"]
TWITTER_OPTIONAL = ["twitter:title", "twitter:description", "twitter:image"]
TWITTER_CARD_TYPES = {"summary", "summary_large_image", "player", "app"}


def _get_meta(soup: BeautifulSoup, attr: str, name: str) -> Optional[str]:
    """Ambil konten meta berdasarkan attr (name/property), case-insensitive."""
    for meta in soup.find_all("meta"):
        if (meta.get(attr) or "").lower() == name.lower():
            value = (meta.get("content") or "").strip()
            return value or None
    return None


def analyze_og_twitter(soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    """Kumpulkan semua nilai tag OG dan Twitter Card dari soup.

    Returns:
        dict tag -> nilai (None bila tidak ada / kosong).
    """
    tags: Dict[str, Optional[str]] = {}
    for name in OG_REQUIRED + OG_OPTIONAL:
        tags[name] = _get_meta(soup, "property", name)
    # og:* bisa juga ditulis sebagai name= (non-standar tapi umum)
    for name in OG_REQUIRED + OG_OPTIONAL:
        if tags[name] is None:
            tags[name] = _get_meta(soup, "name", name)
    for name in TWITTER_REQUIRED + TWITTER_OPTIONAL:
        tags[name] = _get_meta(soup, "name", name)
    return tags


def og_twitter_recommendations(tags: Dict[str, Optional[str]]) -> List[str]:
    """Buat daftar rekomendasi berdasarkan tag yang hilang/tidak valid."""
    recs: List[str] = []
    for name in OG_REQUIRED:
        if tags.get(name) is None:
            recs.append(f"Tambahkan <meta property=\"{name}\" content=\"...\"> (wajib untuk Open Graph)")
    for name in OG_OPTIONAL:
        if tags.get(name) is None:
            recs.append(f"Pertimbangkan <meta property=\"{name}\" content=\"...\"> (opsional, memperkaya preview)")
    card = tags.get("twitter:card")
    if card is None:
        recs.append('Tambahkan <meta name="twitter:card" content="summary|summary_large_image"> (wajib untuk Twitter Card)')
    elif card not in TWITTER_CARD_TYPES:
        recs.append(f"Nilai twitter:card tidak valid: {card!r} (harus salah satu dari {sorted(TWITTER_CARD_TYPES)})")
    for name in TWITTER_OPTIONAL:
        if tags.get(name) is None:
            recs.append(f"Pertimbangkan <meta name=\"{name}\" content=\"...\"> (opsional)")
    return recs


def check_og_twitter() -> None:
    """Interactive: report OG/Twitter Card completeness of a page."""
    from ..core.ui import GREEN, RED, ask_url, fail, header, paint, success, warn

    print(header("Open Graph / Twitter Card", "Social preview metadata"))
    url = ask_url()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return

    tags = analyze_og_twitter(soup)
    print()
    print(paint("  Open Graph:", GREEN))
    for name in OG_REQUIRED + OG_OPTIONAL:
        value = tags[name]
        mark = paint("OK      ", GREEN) if value else paint("MISSING ", RED)
        print(f"    {mark} {name:<22} {value or '-'}")
    print(paint("  Twitter Card:", GREEN))
    for name in TWITTER_REQUIRED + TWITTER_OPTIONAL:
        value = tags[name]
        mark = paint("OK      ", GREEN) if value else paint("MISSING ", RED)
        print(f"    {mark} {name:<22} {value or '-'}")

    recs = og_twitter_recommendations(tags)
    print()
    if recs:
        print(warn("Recommendations:"))
        for i, rec in enumerate(recs, 1):
            print(f"    {i}. {rec}")
    else:
        print(success("All OG and Twitter Card tags are present."))
