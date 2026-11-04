"""Analisis kecepatan muat gambar."""

import time
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..core.ui import GREEN, RED, ask_url, fail, header, label_value, paint, warn
from ..core.http import get_session
from .fetch import fetch_page, parse_soup


def resolve_img_url(img_tag, base_url: str) -> Optional[str]:
    """Find the effective image URL, lazy-load aware.

    Lazy attributes (data-src etc.) take priority over 'src' because on
    lazy images 'src' usually holds a tiny placeholder.
    """
    for attr in ("data-src", "data-original", "data-lazy-src", "src"):
        value = (img_tag.get(attr) or "").strip()
        if value and not value.startswith("data:"):
            return urljoin(base_url, value)
    srcset = (img_tag.get("srcset") or img_tag.get("data-srcset") or "").strip()
    if srcset:
        first = srcset.split(",")[0].strip().split(" ")[0]
        if first and not first.startswith("data:"):
            return urljoin(base_url, first)
    return None


def measure_image(url: str, timeout: tuple = (10, 30)) -> dict:
    """Download an image fully and measure time + size."""
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
    """Collect unique image URLs (including lazy) from soup."""
    urls = []
    seen = set()
    for img in soup.find_all("img"):
        resolved = resolve_img_url(img, base_url)
        if resolved and resolved not in seen:
            seen.add(resolved)
            urls.append(resolved)
    return urls


def analyze_image_load_speed() -> None:
    """Interactive: measure load time of every image on a page."""
    from ..core.ui import ask_url, fail, header, label_value, paint, GREEN, warn

    print(header("Image Load Speed", "Full-download timing per image"))
    url = ask_url()
    try:
        response = fetch_page(url)
        response.raise_for_status()
        soup = parse_soup(response.content)
    except Exception as e:
        print(fail(f"Request failed: {url}: {e}"))
        return

    images = collect_image_urls(soup, response.url)
    if not images:
        print(warn("No images found on this page."))
        return

    print(f"\n  Measuring {len(images)} images...")
    total_size = 0
    for i, img_url in enumerate(images, 1):
        result = measure_image(img_url)
        if result["error"]:
            print(f"  {paint('[FAIL]', RED)} {img_url} — {result['error']}")
        else:
            total_size += result["size"]
            print(f"  {paint(f'{i:>3}.', GREEN)} {img_url}")
            print(f"        {result['size'] // 1024} KB in {result['load_time']:.2f}s")
    print()
    print(label_value("Images", len(images)))
    print(label_value("Total weight", f"{total_size // 1024} KB"))
