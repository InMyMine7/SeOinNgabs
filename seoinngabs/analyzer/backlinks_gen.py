"""Backlink generator."""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from urllib.parse import urlparse

from ..core.http import get_session
from ..core.ui import GREEN, RED, ask, fail, header, label_value, paint, progress_done, progress_inline
from ..core.url import is_valid_domain
from ..data import BACKLINK_DB

WORKERS = 8
PLACEHOLDER = "inmymine7"


def load_backlink_sites() -> List[str]:
    """Load URL templates from backlink.json (absolute path)."""
    with BACKLINK_DB.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [entry["url"] for entry in data if entry.get("url")]


def check_backlink_url(url: str) -> dict:
    """Check a single backlink URL; never raises."""
    try:
        response = get_session().get(url, timeout=(10, 20))
        return {"url": url, "status": response.status_code, "error": None}
    except Exception as e:
        return {"url": url, "status": None, "error": str(e)}


def generate_backlinks() -> None:
    """Interactive: submit a domain to the list of backlink sites."""
    print(header("Backlink Generator", "Submit your domain to stat/whois sites"))
    site = ask("Domain name (e.g. example.com)").strip().lower()

    if not site:
        print(fail("No domain entered."))
        return
    if not is_valid_domain(site):
        print(fail(f"Invalid domain: {site!r} (example: example.com)"))
        return

    try:
        templates = load_backlink_sites()
    except (OSError, ValueError) as e:
        print(fail(f"Could not load backlink.json: {e}"))
        return

    try:
        limit = int(ask("How many sites to check (0 = all)", "50"))
    except ValueError:
        limit = 50
    if limit > 0:
        templates = templates[:limit]

    print(f"\n  Checking {len(templates)} backlink sites (parallel, rate-limited)...")

    def worker(template: str) -> dict:
        url = template.replace(PLACEHOLDER, site)
        result = check_backlink_url(url)
        result["domain"] = urlparse(url).netloc
        return result

    ok = fail_count = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(worker, t) for t in templates]
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            status = result["status"] if result["status"] is not None else "FAILED"
            mark = paint(f"{status:>7}", GREEN if result["status"] is not None else RED)
            print(f"  {result['domain']:<40} {mark}")
            if result["status"] is not None:
                ok += 1
            else:
                fail_count += 1
            progress_inline(i, len(futures), every=25, label="sites")
    progress_done()
    print()
    print(label_value("Done", f"{ok} succeeded, {fail_count} failed of {len(templates)} sites"))
