"""Analisis kecepatan muat gambar (fix J1-J6).

Perbaikan vs main.py lama:
- Body benar-benar diunduh via iter_content — waktu + ukuran nyata (fix J1).
- Normalisasi scheme (fix J2) dan penggabungan URL via urljoin (fix J4:
  'page.html' + 'img.png' dan '//cdn' sekarang benar).
- Lazy-load: data-src / data-original / srcset dikenali (fix J3).
- Timeout/UA via session (fix J5).
- Pesan gagal berwarna merah, PEP 8 (fix J6).
"""

import time
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..core.http import get_session
from ..core.output import colorize
from .fetch import fetch_page, parse_soup


def resolve_img_url(img_tag, base_url: str) -> Optional[str]:
    """Cari URL gambar efektif dengan dukungan lazy-load (fix J3).

    Atribut lazy-load (data-src dst.) dicek duluan: pada gambar lazy, 'src'
    biasanya hanya placeholder kecil sedangkan URL asli ada di data-src.
    """
    for attr in ("data-src", "data-original", "data-lazy-src", "src"):
        value = (img_tag.get(attr) or "").strip()
        if value and not value.startswith("data:"):
            return urljoin(base_url, value)
    srcset = (img_tag.get("srcset") or img_tag.get("data-srcset") or "").strip()
    if srcset:
        # Ambil kandidat pertama dari srcset: "url 1x, url 2x, ..."
        first = srcset.split(",")[0].strip().split(" ")[0]
        if first and not first.startswith("data:"):
            return urljoin(base_url, first)
    return None


def measure_image(url: str, timeout: tuple = (10, 30)) -> dict:
    """Unduh gambar penuh, ukur waktu + ukuran (fix J1)."""
    session = get_session()
    start = time.monotonic()
    size = 0
    try:
        with session.get(url, stream=True, timeout=timeout) as response:
            if response.status_code != 200:
                return {"url": url, "error": f"HTTP {response.status_code}", "size": 0, "load_time": None}
            for chunk in response.iter_content(chunk_size=8192):
                size += len(chunk)
        load_time = time.monotonic() - start
        return {"url": url, "error": None, "size": size, "load_time": load_time}
    except Exception as e:
        return {"url": url, "error": str(e), "size": 0, "load_time": None}


def collect_image_urls(soup, base_url: str) -> List[str]:
    """Kumpulkan URL gambar unik (termasuk lazy-load) dari soup."""
    urls = []
    seen = set()
    for img in soup.find_all("img"):
        resolved = resolve_img_url(img, base_url)
        if resolved and resolved not in seen:
            seen.add(resolved)
            urls.append(resolved)
    return urls


def analyze_image_load_speed() -> None:
    """Menu interaktif: ukur waktu muat semua gambar di halaman."""
    print("===== Analyze Image Load Speed =====")
    url = input("\nMasukkan URL halaman: ").strip()
    try:
        response = fetch_page(url)
        response.raise_for_status()
        soup = parse_soup(response.content)
    except Exception as e:
        print(colorize(f"Gagal memeriksa kecepatan gambar untuk {url}: {e}", "red"))
        return

    images = collect_image_urls(soup, response.url)
    if not images:
        print(colorize("Tidak ada gambar ditemukan di halaman.", "green"))
        return

    for img_url in images:
        result = measure_image(img_url)
        if result["error"]:
            print(colorize(f"Gagal memuat gambar di {img_url} ({result['error']})", "red"))
        else:
            print(
                colorize(
                    "Gambar di {} ({} KB) memuat dalam waktu {:.2f} detik".format(
                        img_url, result["size"] // 1024, result["load_time"]
                    ),
                    "green",
                )
            )
