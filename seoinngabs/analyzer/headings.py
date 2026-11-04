"""Pemeriksa heading h1-h6 (fix F1-F4).

Baru: deteksi h1 ganda, lompatan level, heading kosong — sambil tetap
mencetak semua heading seperti perilaku lama.
"""

from typing import List, Tuple

from bs4 import BeautifulSoup

from ..core.output import COLORS, colorize
from .fetch import fetch_page, parse_soup


def analyze_headings(soup: BeautifulSoup) -> dict:
    """Analisis struktur heading.

    Returns:
        dict: headings (list (tag, teks)), h1_count, empty_headings,
        skipped_levels (list pesan lompatan).
    """
    headings: List[Tuple[str, str]] = []
    empty: List[str] = []
    skipped: List[str] = []
    prev_level = 0

    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        level = int(tag.name[1])
        text = tag.get_text(" ", strip=True)
        headings.append((tag.name, text))
        if not text:
            empty.append(tag.name)
        if level > prev_level + 1 and prev_level != 0:
            skipped.append(f"h{prev_level} -> h{level} ({text or '(kosong)'})")
        prev_level = level

    h1_count = sum(1 for name, _ in headings if name == "h1")
    return {
        "headings": headings,
        "h1_count": h1_count,
        "empty_headings": empty,
        "skipped_levels": skipped,
    }


def check_headings() -> None:
    """Menu interaktif: cetak semua heading + peringatan struktur."""
    print("=====h1, h2, h3, h4, h5, h6 checker=====")
    url = input("\nMasukkan URL halaman: ").strip()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print("Terjadi kesalahan permintaan:", e)
        return

    result = analyze_headings(soup)
    for name, text in result["headings"]:
        color = COLORS.get(name, COLORS["reset"])
        print(f"{color}{name}: {text or '(kosong)'}{COLORS['reset']}")

    if result["h1_count"] == 0:
        print(colorize("\n[!] Tidak ada h1 di halaman ini.", "red"))
    elif result["h1_count"] > 1:
        print(colorize(f"\n[!] Ditemukan {result['h1_count']} h1 — sebaiknya hanya satu.", "red"))
    if result["empty_headings"]:
        print(colorize(f"[!] Heading kosong: {', '.join(result['empty_headings'])}", "red"))
    for s in result["skipped_levels"]:
        print(colorize(f"[!] Lompatan level: {s}", "red"))
