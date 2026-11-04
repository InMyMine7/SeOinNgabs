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
    """Interactive: report the alt attribute of every image."""
    from ..core.ui import GREEN, RED, ask_url, fail, header, label_value, paint, success, warn

    print(header("Image Alt Checker", "Accessibility & SEO alt attributes"))
    url = ask_url()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return

    results = analyze_image_alts(soup, response.url)
    if not results:
        print(warn("No images found on this page."))
        return

    for r in results:
        if r["status"] == "ok":
            print(f"  {paint('[OK]     ', GREEN)} {r['url']}")
            print(f"           alt: {r['alt']}")
        elif r["status"] == "missing":
            print(f"  {paint('[MISSING]', RED)} {r['url']}")
            print(f"           alt: (attribute not present)")
        elif r["status"] == "empty":
            print(f"  {paint('[EMPTY]  ', RED)} {r['url']}")
            print(f"           alt: \"\" (decorative only)")
        else:
            print(f"  {paint('[LONG]   ', RED)} {r['url']}")
            print(f"           alt ({len(r['alt'])} chars, max {MAX_ALT_LENGTH}): {r['alt'][:80]}...")

    summary = alt_summary(results)
    print()
    print(label_value("Images", summary["total"]))
    print(label_value("With alt", summary["ok"]))
    print(label_value("Missing alt", summary["missing"]))
    print(label_value("Empty alt", summary["empty"]))
    print(label_value("Too long", summary["long"]))
    if summary["missing"] > 0:
        print(warn("Recommendation: add descriptive alt text to every meaningful image."))
    elif summary["missing"] == 0:
        print(success("All images have alt text."))
