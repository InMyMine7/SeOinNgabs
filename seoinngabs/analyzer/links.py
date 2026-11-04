"""Analisis backlink internal/eksternal + anchor text."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..core.http import get_session
from ..core.ui import GREEN, YELLOW, ask_url, fail, header, paint
from ..core.url import join_url, same_site
from .fetch import fetch_page, parse_soup

SKIP_PREFIXES = ("mailto:", "tel:", "javascript:", "#", "data:", "sms:")
WORKERS = 8


def classify_links(url: str, soup: BeautifulSoup, include_subdomains: bool = False) -> dict:
    """Classify all <a href> into internal/external.

    Returns:
        dict: internal, external (list of dict: href, anchor, nofollow),
        skipped (list of non-http hrefs).
    """
    internal = []
    external = []
    skipped = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href or href.startswith(SKIP_PREFIXES):
            if href and not href.startswith("#"):
                skipped.append(href)
            continue
        absolute = join_url(url, href)
        if not urlparse(absolute).scheme.startswith("http"):
            skipped.append(href)
            continue
        key = (absolute.split("#")[0], a.get_text(" ", strip=True))
        if key in seen:
            continue
        seen.add(key)
        rel = a.get("rel")
        rel_values = " ".join(rel).lower() if isinstance(rel, list) else (rel or "").lower()
        entry = {
            "href": absolute.split("#")[0],
            "anchor": a.get_text(" ", strip=True),
            "nofollow": "nofollow" in rel_values,
        }
        if same_site(url, absolute, include_subdomains=include_subdomains):
            internal.append(entry)
        else:
            external.append(entry)

    return {"internal": internal, "external": external, "skipped": skipped}


def check_link_status(url: str, method: str = "HEAD", timeout: tuple = (10, 20)) -> dict:
    """Check one link with HEAD->GET fallback and redirect info."""
    session = get_session()
    chain: List[tuple] = []
    try:
        response = session.request(method, url, allow_redirects=False, timeout=timeout)
        chain.append((response.status_code, url))
        if response.status_code in (405, 501) and method == "HEAD":
            response.close()
            response = session.request("GET", url, allow_redirects=False, timeout=timeout)
            chain.append((response.status_code, url))
        redirected = 300 <= response.status_code < 400 and bool(response.headers.get("Location"))
        final_url = response.headers.get("Location") or url
        response.close()
        return {
            "status_code": response.status_code,
            "error": None,
            "redirected": redirected,
            "final_url": final_url,
            "chain": chain,
        }
    except Exception as e:
        return {"status_code": None, "error": str(e), "redirected": False, "final_url": url, "chain": chain}


def check_urls_parallel(urls: List[str], workers: int = WORKERS, progress: bool = True) -> List[dict]:
    """Check many URLs in parallel (bounded) with the rate-limited session."""
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(check_link_status, u): u for u in urls}
        for i, future in enumerate(as_completed(futures), 1):
            url = futures[future]
            results.append({"url": url, **future.result()})
            if progress and i % 10 == 0:
                print(f"  ... {i}/{len(futures)} links checked", end="\r")
    if progress:
        print(" " * 40, end="\r")
    return results


def analyze_backlinks() -> None:
    """Interactive: list internal/external links with anchor text."""
    from ..core.ui import GREEN, ask_url, fail, header, paint

    print(header("Internal/External Links", "Links with anchor text and nofollow"))
    url = ask_url()
    try:
        response = fetch_page(url)
        soup = parse_soup(response.content)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return

    result = classify_links(response.url, soup)
    print()
    print(paint(f"  Internal links ({len(result['internal'])}):", GREEN))
    for link in result["internal"]:
        nofollow = paint(" [nofollow]", YELLOW) if link["nofollow"] else ""
        print(f"    {link['anchor'] or '(no text)'} -> {link['href']}{nofollow}")
    print(paint(f"  External links ({len(result['external'])}):", GREEN))
    for link in result["external"]:
        nofollow = paint(" [nofollow]", YELLOW) if link["nofollow"] else ""
        print(f"    {link['anchor'] or '(no text)'} -> {link['href']}{nofollow}")
