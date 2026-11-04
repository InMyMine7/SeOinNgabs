"""Pemeriksa title, meta description, canonical, dan og:image (fix E1-E6)."""

from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..core.output import colorize
from .fetch import fetch_page, parse_soup


def _meta_content(soup: BeautifulSoup, attr: str, value: str) -> Optional[str]:
    """Ambil konten meta dengan nama/property case-insensitive (fix E2) dan
    aman dari tag tanpa atribut content (fix E1)."""
    for meta in soup.find_all("meta"):
        if (meta.get(attr) or "").lower() == value.lower() and meta.get("content") is not None:
            return meta.get("content")
    return None


def _canonical_href(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Ambil href canonical, case-insensitive, di-resolve ke absolute (fix E1, E2, E3)."""
    for link in soup.find_all("link"):
        rel = link.get("rel")
        rel_values = rel if isinstance(rel, list) else [rel or ""]
        if any(str(v).lower() == "canonical" for v in rel_values) and link.get("href") is not None:
            return urljoin(base_url, link.get("href", "").strip())
    return None


def extract_page_meta(url: str) -> dict:
    """Ekstrak title, meta description, canonical, og:image dari halaman.

    Returns:
        dict berisi: status, title, meta_description, canonical, og_image,
        base_url (URL final setelah redirect).
    """
    response = fetch_page(url)
    soup = parse_soup(response.content)
    base_url = response.url

    title_tag = soup.title
    title = title_tag.get_text(strip=True) if title_tag else None
    if title is not None and not title:
        title = None  # <title>   </title> dianggap kosong (fix E4)

    return {
        "status": response.status_code,
        "base_url": base_url,
        "title": title,
        "meta_description": _meta_content(soup, "name", "description"),
        "canonical": _canonical_href(soup, base_url),
        "og_image": _meta_content(soup, "property", "og:image"),
    }


def check_title_meta_canonical() -> None:
    """Menu interaktif: tampilkan title/meta/canonical/og:image halaman."""
    print("=====Check Title, Meta, URL Canonical=====")
    url = input("\nMasukkan URL halaman: ").strip()
    try:
        meta = extract_page_meta(url)
    except Exception as e:  # requests.RequestException + InvalidURLError
        print("Terjadi kesalahan permintaan:", e)
        return
    print(f"\n{colorize('Judul:', 'red')} {meta['title'] or 'N/A'}")
    print(f"{colorize('Meta Deskripsi:', 'red')} {meta['meta_description'] or 'N/A'}")
    print(f"{colorize('URL Canonical:', 'red')} {meta['canonical'] or 'N/A'}")
    print(f"{colorize('Gambar OG:', 'red')} {meta['og_image'] or 'N/A'}")
