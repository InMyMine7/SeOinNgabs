"""Broken link checker (fix H1-H6).

Perbaikan vs main.py lama:
- Semua href di-resolve dengan urljoin sebelum dicek (fix H1: '/' tidak lagi
  MissingSchema -> broken palsu).
- Paralel + rate limit + timeout (fix H2).
- HEAD dengan fallback GET untuk 405/501 (fix H3) dan klasifikasi 403/999
  sebagai 'perlu review' bukan langsung broken (fix H5 via UA + klasifikasi).
- Duplikat di-dedup (fix H6).
"""

from typing import List

from bs4 import BeautifulSoup

from ..core.output import colorize
from ..core.url import join_url
from .fetch import fetch_page, parse_soup
from .links import classify_links, check_urls_parallel


def collect_links(url: str, soup: BeautifulSoup) -> List[str]:
    """Kumpulkan href absolut unik dari soup (dedup, skip non-http)."""
    result = classify_links(url, soup)
    return sorted({link["href"] for link in result["internal"] + result["external"]})


def check_broken_links() -> None:
    """Menu interaktif: temukan broken links di halaman."""
    print("=====Check Broken Links=====")
    url = input("\nMasukkan URL halaman: ").strip()
    print("Tunggu sebentar proses ini memakan waktu cukup lama")
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print("Terjadi kesalahan permintaan:", e)
        return

    links = collect_links(response.url, soup)
    if not links:
        print(colorize("\nTidak ada link yang dapat diperiksa.", "green"))
        return

    results = check_urls_parallel(links)

    broken = [r for r in results if r["error"] is None and r["status_code"] >= 400]
    review = [r for r in results if r["error"] is None and r["status_code"] in (403, 999)]
    errors = [r for r in results if r["error"] is not None]

    if broken or review or errors:
        print(colorize("\nTautan bermasalah ditemukan:", "red"))
        for r in broken:
            print(f"[BROKEN {r['status_code']}] {r['url']}")
        for r in review:
            print(f"[REVIEW {r['status_code']}] {r['url']} (403/999 — bisa jadi bot-block, cek manual)")
        for r in errors:
            print(f"[ERROR] {r['url']} ({r['error']})")
    else:
        print(colorize("\nTidak ada tautan yang rusak ditemukan.", "green"))
