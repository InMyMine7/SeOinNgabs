"""Redirect chain tracer (Tahap 4 fitur #4).

Menelusuri rantai redirect dari URL awal sampai tujuan akhir:
- Setiap hop: status code + URL + header Location
- Deteksi redirect loop (URL berulang atau > MAX_HOPS)
- Distinguish 301/302/303/307/308
- Tidak memakai allow_redirects requests — hop manual agar chain terlihat.
"""

from typing import Dict, List, Optional

from ..core.http import get_session
from ..core.output import colorize
from ..core.url import normalize_url

MAX_HOPS = 10
REDIRECT_CODES = {301, 302, 303, 307, 308}


def trace_redirects(url: str, max_hops: int = MAX_HOPS) -> Dict:
    """Telusuri rantai redirect dari url.

    Returns:
        dict: hops (list of {status, url, location}), final_url, total_hops,
        loop (bool), completed (bool — sampai non-redirect atau loop/max).
    """
    session = get_session()
    current = normalize_url(url)
    hops: List[Dict] = []
    visited = {current}
    loop = False
    completed = False

    for _ in range(max_hops):
        try:
            response = session.request("GET", current, allow_redirects=False, timeout=(10, 20))
        except Exception as e:
            hops.append({"status": None, "url": current, "location": None, "error": str(e)})
            return {"hops": hops, "final_url": current, "total_hops": len(hops), "loop": False, "completed": False}

        status = response.status_code
        location = response.headers.get("Location")
        hops.append({"status": status, "url": current, "location": location, "error": None})
        response.close()

        if status not in REDIRECT_CODES or not location:
            completed = True
            break

        from urllib.parse import urljoin

        next_url = urljoin(current, location)
        if next_url in visited:
            loop = True
            break
        visited.add(next_url)
        current = next_url

    return {
        "hops": hops,
        "final_url": hops[-1]["url"] if hops else current,
        "total_hops": len(hops),
        "loop": loop,
        "completed": completed,
    }


def trace_redirects_interactive() -> None:
    """Interactive: trace and display the redirect chain."""
    from ..core.ui import GREEN, RED, ask_url, fail, header, label_value, paint, success, warn

    print(header("Redirect Chain Tracer", "Hop-by-hop redirect trail"))
    url = ask_url()
    try:
        result = trace_redirects(url)
    except Exception as e:
        print(fail(f"Request failed: {e}"))
        return

    print()
    print(label_value("Total hops", result["total_hops"]))
    for i, hop in enumerate(result["hops"], 1):
        if hop["error"]:
            print(f"  {i}. {paint('ERROR', RED)} {hop['url']} — {hop['error']}")
            continue
        status = hop["status"]
        mark = paint(f"{status}", RED if status in REDIRECT_CODES else GREEN)
        line = f"  {i}. [{mark}] {hop['url']}"
        if hop["location"]:
            line += f"\n       -> {hop['location']}"
        print(line)

    print()
    if result["loop"]:
        print(warn("LOOP DETECTED — redirects back to an already visited URL."))
    elif not result["completed"]:
        print(warn(f"Chain cut off: exceeded {MAX_HOPS} hops."))
    else:
        final_hop = result["hops"][-1]
        if final_hop["status"] in REDIRECT_CODES or final_hop["status"] is None:
            print(warn(f"Ended at status {final_hop['status']} without a Location header."))
        else:
            print(success(f"OK — ends at {result['final_url']} (status {final_hop['status']})."))
