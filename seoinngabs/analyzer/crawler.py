"""Site crawler (Tahap 4 fitur #5).

Crawl internal satu situs dengan:
- Batas depth dan jumlah halaman
- Menghormati robots.txt (Disallow/Allow + Crawl-delay)
- Rate limit minimum antar request (session + jeda ekstra)
- Hanya halaman HTML (Content-Type), link internal saja (same_site)
- BFS agar page limit terpenuhi merata
"""

import time
from collections import deque
from typing import Dict, List, Optional
from urllib.parse import urldefrag, urljoin, urlparse

from ..core.http import get_session
from ..core.output import colorize
from ..core.url import normalize_url, same_site
from .fetch import parse_soup
from .links import SKIP_PREFIXES
from .robots_parser import fetch_robots_txt

CRAWLER_UA = "SeOinNgabsBot"
MIN_DELAY = 0.5  # detik minimum antar halaman (di atas rate limit session)


def crawl_site(
    start_url: str,
    max_depth: int = 2,
    max_pages: int = 20,
    respect_robots: bool = True,
    delay: Optional[float] = None,
) -> List[Dict]:
    """Crawl situs dari start_url (BFS, dibatasi depth dan page).

    Returns:
        List of dict: url, status, depth, links (jumlah link keluar),
        error (None bila OK).
    """
    start = normalize_url(start_url)
    base_domain = urlparse(start).hostname or ""
    robots = fetch_robots_txt(start, user_agent=CRAWLER_UA) if respect_robots else None
    crawl_delay = robots.get_crawl_delay(CRAWLER_UA) if robots else None
    effective_delay = delay if delay is not None else max(MIN_DELAY, crawl_delay or 0)

    queue = deque([(urldefrag(start)[0], 0)])
    visited = set()
    results: List[Dict] = []
    last_request_time = 0.0

    while queue and len(results) < max_pages:
        url, depth = queue.popleft()
        if url in visited or depth > max_depth:
            continue
        visited.add(url)

        if robots and not robots.is_allowed("/" + urlparse(url).path.lstrip("/"), CRAWLER_UA):
            results.append({"url": url, "status": "robots-disallow", "depth": depth, "links": 0, "error": None})
            continue

        # rate limit ekstra crawler
        now = time.monotonic()
        wait = effective_delay - (now - last_request_time)
        if wait > 0:
            time.sleep(wait)
        last_request_time = time.monotonic()

        try:
            response = get_session().get(url, timeout=(10, 30))
        except Exception as e:
            results.append({"url": url, "status": None, "depth": depth, "links": 0, "error": str(e)})
            continue

        content_type = response.headers.get("Content-Type", "")
        if response.status_code == 200 and "text/html" in content_type:
            soup = parse_soup(response.content)
            found = 0
            for a in soup.find_all("a", href=True):
                href = (a.get("href") or "").strip()
                if not href or href.startswith(SKIP_PREFIXES):
                    continue
                absolute = urldefrag(urljoin(response.url, href))[0]
                if not same_site(start, absolute):
                    continue
                if absolute not in visited and depth < max_depth:
                    queue.append((absolute, depth + 1))
                found += 1
            results.append({"url": url, "status": 200, "depth": depth, "links": found, "error": None})
        else:
            results.append({"url": url, "status": response.status_code, "depth": depth, "links": 0, "error": None})

    return results


def crawl_site_interactive() -> None:
    """Interactive: crawl a site and report results."""
    from ..core.ui import GREEN, RED, ask_int, ask_url, fail, header, label_value, paint, warn

    print(header("Site Crawler", "BFS crawl honoring robots.txt and rate limits"))
    url = ask_url("Start URL")
    depth = ask_int("Max depth", 2, minimum=0, maximum=10)
    pages = ask_int("Max pages", 20, minimum=1, maximum=500)

    print(f"\n  Crawling {url} (depth={depth}, max {pages} pages, robots.txt honored)...")
    try:
        results = crawl_site(url, max_depth=depth, max_pages=pages)
    except Exception as e:
        print(fail(f"Crawl failed: {e}"))
        return

    if not results:
        print(warn("No pages were crawled."))
        return

    for r in results:
        depth = r["depth"]
        if r["error"]:
            print(f"  {paint(f'[ERROR d{depth}]', RED)} {r['url']} — {r['error']}")
        elif r["status"] == "robots-disallow":
            print(f"  {paint('[ROBOTS]', RED)} {r['url']} (blocked by robots.txt)")
        elif r["status"] == 200:
            print(f"  {paint(f'[OK d{depth}]', GREEN)} {r['url']} ({r['links']} links)")
        else:
            print(f"  {paint(f'[{r['status']} d{depth}]', RED)} {r['url']}")

    ok = sum(1 for r in results if r["status"] == 200)
    print()
    print(label_value("Pages OK", f"{ok}/{len(results)}"))
    print(label_value("Max depth reached", max(r["depth"] for r in results)))
