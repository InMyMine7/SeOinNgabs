"""Backlink generator (fix C1-C5).

Perbaikan vs main.py lama:
- Path backlink.json di-resolve absolut via package (fix C2).
- Validasi nama domain (fix C4).
- Domain diekstrak via urlparse — aman untuk https (fix C3).
- Paralel + rate limit + timeout + progress (fix C1).
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from urllib.parse import urlparse

from ..core.http import get_session
from ..core.output import colorize
from ..core.url import is_valid_domain
from ..data import BACKLINK_DB

WORKERS = 8
PLACEHOLDER = "inmymine7"


def load_backlink_sites() -> List[str]:
    """Muat daftar template URL dari backlink.json (fix C2: path absolut)."""
    import json

    with BACKLINK_DB.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return [entry["url"] for entry in data if entry.get("url")]


def check_backlink_url(url: str) -> dict:
    """Cek satu URL backlink. Tidak pernah raise — kembalikan dict hasil."""
    try:
        response = get_session().get(url, timeout=(10, 20))
        return {"url": url, "status": response.status_code, "error": None}
    except Exception as e:
        return {"url": url, "status": None, "error": str(e)}


def generate_backlinks() -> None:
    """Menu interaktif: submit domain ke daftar situs backlink."""
    print("=====Backlink Generator=====")
    site = input("Nama domain\t: ").strip().lower()

    if not site:
        print("Anda tidak memasukkan nama domain. Keluar.")
        return
    if not is_valid_domain(site):
        print(colorize(f"Nama domain tidak valid: {site!r} (contoh: example.com)", "red"))
        return

    try:
        templates = load_backlink_sites()
    except (OSError, ValueError) as e:
        print(colorize(f"Gagal memuat backlink.json: {e}", "red"))
        return

    print(f"Memeriksa {len(templates)} situs backlink (paralel, rate-limited)...")

    def worker(template: str) -> dict:
        url = template.replace(PLACEHOLDER, site)
        result = check_backlink_url(url)
        result["domain"] = urlparse(url).netloc
        return result

    ok = fail = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(worker, t) for t in templates]
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            status = result["status"] if result["status"] is not None else "Permintaan gagal"
            print(f"~ {site} | Hasil -> {result['domain']} status: {status}")
            if result["status"] is not None:
                ok += 1
            else:
                fail += 1
            if i % 50 == 0:
                print(f"  ... {i}/{len(futures)} situs", end="\r")

    print(f"\nSelesai: {ok} sukses, {fail} gagal dari {len(templates)} situs.")
