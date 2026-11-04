"""Analisis link 403/301 + redirect chain tracer (fix I1-I4).

Perbaikan vs main.py lama:
- allow_redirects=False sehingga 301 benar-benar terdeteksi (fix I1).
- urljoin untuk link relatif (fix I2) — tidak ada lagi skip diam-diam.
- Deteksi 403 eksplisit (fix I4: nama fitur '403 dan 301' akhirnya sesuai).
- Paralel + timeout (fix I3).
"""

from typing import List, Optional

from bs4 import BeautifulSoup

from ..core.output import colorize
from .fetch import fetch_page, parse_soup
from .links import check_link_status, check_urls_parallel, classify_links


def analyze_404_301_links() -> None:
    """Menu interaktif: daftar link 404 dan 301 di halaman."""
    print("=====Analisa link 404 dan 301=====")
    url = input("\nMasukkan URL halaman: ").strip()
    print("Tunggu sebentar proses ini memakan waktu cukup lama")
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print("Terjadi kesalahan permintaan:", e)
        return

    result = classify_links(response.url, soup)
    links = sorted({l["href"] for l in result["internal"] + result["external"]})
    if not links:
        print(colorize("Tidak ada link yang dapat diperiksa.", "green"))
        return

    statuses = check_urls_parallel(links)

    links_404 = [s for s in statuses if s["status_code"] == 404]
    links_301 = [s for s in statuses if s["status_code"] in (301, 302, 307, 308)]
    links_403 = [s for s in statuses if s["status_code"] == 403]

    for label, items, code_hint in [
        ("404", links_404, "Tautan internal dengan kode 404 ditemukan"),
        ("301", links_301, "Tautan internal dengan kode 301 ditemukan"),
        ("403", links_403, "Tautan internal dengan kode 403 ditemukan (bot-block?)"),
    ]:
        if items:
            print(colorize(f"\n{code_hint}:", "red"))
            for r in items:
                extra = f" -> {r['final_url']}" if r.get("redirected") else ""
                print(f"{r['url']}{extra}")
        else:
            print(colorize(f"\nTidak ada tautan {label} ditemukan.", "green"))
