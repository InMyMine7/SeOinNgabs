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
    """Menu interaktif: telusuri dan tampilkan rantai redirect."""
    print("=====Redirect Chain Tracer=====")
    url = input("\nMasukkan URL halaman: ").strip()
    try:
        result = trace_redirects(url)
    except Exception as e:
        print("Terjadi kesalahan:", e)
        return

    print(f"\n{colorize('Rantai redirect:', 'green')} {result['total_hops']} hop(s)")
    for i, hop in enumerate(result["hops"], 1):
        if hop["error"]:
            print(f"  {i}. {colorize('ERROR', 'red')} {hop['url']} — {hop['error']}")
            continue
        status = hop["status"]
        color = "red" if status in REDIRECT_CODES else "green"
        line = f"  {i}. [{colorize(str(status), color)}] {hop['url']}"
        if hop["location"]:
            line += f"\n      -> {hop['location']}"
        print(line)

    if result["loop"]:
        print(colorize(f"\n[!] LOOP TERDETEKSI — redirect kembali ke URL yang sudah dikunjungi.", "red"))
    elif not result["completed"]:
        print(colorize(f"\n[!] Rantai terpotong: melebihi {MAX_HOPS} hop.", "red"))
    else:
        final_hop = result["hops"][-1]
        if final_hop["status"] in REDIRECT_CODES or final_hop["status"] is None:
            print(colorize(f"\n[!] Berakhir di status {final_hop['status']} tanpa Location.", "red"))
        else:
            print(colorize(f"\nOK — berakhir di {result['final_url']} (status {final_hop['status']}).", "green"))
