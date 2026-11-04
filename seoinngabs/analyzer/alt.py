"""Image alt checker (Tahap 4 fitur #2).

Memeriksa atribut alt pada semua <img> di halaman:
- alt hilang sama sekali (masalah aksesibilitas & SEO)
- alt kosong (alt="") — sah untuk gambar dekoratif, tapi dilaporkan info
- alt terlalu panjang (>125 karakter, praktik umum screen reader)
- lazy-load: data-src/srcset juga diperiksa (konsisten images.py)
"""

from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..core.output import colorize
from .fetch import fetch_page, parse_soup
from .images import resolve_img_url

MAX_ALT_LENGTH = 125


def analyze_image_alts(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """Kumpulkan status alt tiap gambar.

    Returns:
        List of dict: url, alt (None bila atribut tidak ada), status
        ('ok' | 'missing' | 'empty' | 'long').
    """
    results: List[Dict] = []
    seen = set()
    for img in soup.find_all("img"):
        src = resolve_img_url(img, base_url)
        if src is None or src in seen:
            continue
        seen.add(src)
        if not img.has_attr("alt"):
            status = "missing"
        elif not img.get("alt", "").strip():
            status = "empty"
        elif len(img.get("alt", "")) > MAX_ALT_LENGTH:
            status = "long"
        else:
            status = "ok"
        results.append({
            "url": src,
            "alt": img.get("alt") if img.has_attr("alt") else None,
            "status": status,
        })
    return results


def alt_summary(results: List[Dict]) -> Dict[str, int]:
    """Ringkasan jumlah per status."""
    counts = {"ok": 0, "missing": 0, "empty": 0, "long": 0, "total": len(results)}
    for r in results:
        counts[r["status"]] += 1
    return counts


def check_image_alts() -> None:
    """Menu interaktif: laporkan atribut alt semua gambar."""
    print("=====Image Alt Checker=====")
    url = input("\nMasukkan URL halaman: ").strip()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print("Terjadi kesalahan permintaan:", e)
        return

    results = analyze_image_alts(soup, response.url)
    if not results:
        print(colorize("Tidak ada gambar ditemukan di halaman.", "green"))
        return

    for r in results:
        if r["status"] == "ok":
            print(f"  [{colorize('OK', 'green')}] {r['url']}")
            print(f"        alt: {r['alt']}")
        elif r["status"] == "missing":
            print(f"  [{colorize('MISSING', 'red')}] {r['url']}")
            print(f"        alt: (tidak ada atribut alt)")
        elif r["status"] == "empty":
            print(f"  [{colorize('EMPTY', 'red')}] {r['url']}")
            print(f"        alt: \"\" (kosong — hanya cocok untuk gambar dekoratif)")
        else:
            print(f"  [{colorize('LONG', 'red')}] {r['url']}")
            print(f"        alt ({len(r['alt'])} karakter, maks {MAX_ALT_LENGTH}): {r['alt'][:80]}...")

    summary = alt_summary(results)
    print(f"\n{colorize('Ringkasan:', 'green')} {summary['total']} gambar — "
          f"{summary['ok']} OK, {summary['missing']} tanpa alt, "
          f"{summary['empty']} alt kosong, {summary['long']} terlalu panjang.")
    if summary["missing"] > 0:
        print(colorize("Rekomendasi: tambahkan atribut alt deskriptif pada semua gambar bermakna.", "red"))
