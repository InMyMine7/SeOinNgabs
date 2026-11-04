"""Pemeriksa title, meta description, canonical, dan og:image."""

from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .fetch import fetch_page, parse_soup


def _meta_content(soup: BeautifulSoup, attr: str, value: str) -> Optional[str]:
    """Meta content lookup, case-insensitive, KeyError-safe."""
    for meta in soup.find_all("meta"):
        if (meta.get(attr) or "").lower() == value.lower() and meta.get("content") is not None:
            return meta.get("content")
    return None


def _canonical_href(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """Canonical href, case-insensitive, resolved to absolute."""
    for link in soup.find_all("link"):
        rel = link.get("rel")
        rel_values = rel if isinstance(rel, list) else [rel or ""]
        if any(str(v).lower() == "canonical" for v in rel_values) and link.get("href") is not None:
            return urljoin(base_url, link.get("href", "").strip())
    return None


def extract_page_meta(url: str) -> dict:
    """Extract title, meta description, canonical, og:image from a page."""
    response = fetch_page(url)
    soup = parse_soup(response.content)
    base_url = response.url

    title_tag = soup.title
    title = title_tag.get_text(strip=True) if title_tag else None
    if title is not None and not title:
        title = None

    return {
        "status": response.status_code,
        "base_url": base_url,
        "title": title,
        "meta_description": _meta_content(soup, "name", "description"),
        "canonical": _canonical_href(soup, base_url),
        "og_image": _meta_content(soup, "property", "og:image"),
    }


def check_title_meta_canonical() -> None:
    """Interactive: show title/meta/canonical/og:image of a page."""
    from ..core.ui import ask_url, fail, header, label_value

    print(header("Title, Meta & Canonical", "Head metadata of a page"))
    url = ask_url()
    try:
        meta = extract_page_meta(url)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return
    print()
    print(label_value("Title", meta["title"]))
    print(label_value("Meta description", meta["meta_description"]))
    print(label_value("Canonical URL", meta["canonical"]))
    print(label_value("OG image", meta["og_image"]))
