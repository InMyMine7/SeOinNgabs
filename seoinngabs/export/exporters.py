"""Export hasil analisis ke CSV / JSON / HTML (Tahap 4 fitur #8).

Tiga format dengan struktur data tabel generik (list of dict):
- CSV  : kolom dari union semua key, aman untuk karakter koma/kutip
- JSON : list of dict, indentasi 2, unicode utuh
- HTML : tabel sederhana dengan header, siap dibuka browser

Mode batch: pemrosesan banyak URL sekaligus (paralel, rate-limited).
"""

import csv
import html
import io
import json
from pathlib import Path
from typing import Callable, Dict, List

from ..analyzer.fetch import fetch_page, parse_soup
from ..core.output import colorize


def rows_to_csv(rows: List[Dict]) -> str:
    """Render list of dict menjadi CSV (union kolom, deterministik)."""
    if not rows:
        return ""
    fieldnames: List[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: _to_cell(row.get(k)) for k in fieldnames})
    return buffer.getvalue()


def rows_to_json(rows: List[Dict]) -> str:
    """Render list of dict menjadi JSON indentasi."""
    return json.dumps(rows, indent=2, ensure_ascii=False, default=str)


def rows_to_html(rows: List[Dict], title: str = "Laporan") -> str:
    """Render list of dict menjadi tabel HTML."""
    fieldnames: List[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    esc = html.escape
    parts = [f"<html><head><meta charset='utf-8'><title>{esc(title)}</title></head><body>"]
    parts.append(f"<h1>{esc(title)}</h1>")
    parts.append(f"<p>{len(rows)} baris</p>")
    parts.append("<table border='1' cellpadding='4' cellspacing='0'>")
    parts.append("<tr>" + "".join(f"<th>{esc(str(f))}</th>" for f in fieldnames) + "</tr>")
    for row in rows:
        cells = "".join(f"<td>{esc(_to_cell(row.get(f)))}</td>" for f in fieldnames)
        parts.append(f"<tr>{cells}</tr>")
    parts.append("</table></body></html>")
    return "\n".join(parts)


def export_rows(rows: List[Dict], output_path: str, fmt: str = "csv") -> Path:
    """Simpan rows ke file sesuai format.

    Args:
        rows: data tabel.
        output_path: path file tujuan (ekstensi ditambahkan bila belum cocok).
        fmt: 'csv' | 'json' | 'html'.

    Returns:
        Path file yang ditulis.

    Raises:
        ValueError: format tidak dikenal.
    """
    fmt = fmt.lower().lstrip(".")
    if fmt not in ("csv", "json", "html"):
        raise ValueError(f"Format tidak didukung: {fmt!r} (pilih csv/json/html)")

    path = Path(output_path)
    if path.suffix.lower().lstrip(".") != fmt:
        path = path.with_suffix(f".{fmt}")

    if fmt == "csv":
        content = rows_to_csv(rows)
    elif fmt == "json":
        content = rows_to_json(rows)
    else:
        content = rows_to_html(rows, title=path.stem)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _to_cell(value) -> str:
    """Konversi nilai sel menjadi string yang aman untuk CSV/HTML."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "; ".join(_to_cell(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def batch_analyze(
    urls: List[str],
    analyzer: Callable,
    workers: int = 4,
    progress: bool = True,
) -> List[Dict]:
    """Jalankan analyzer(response, soup) -> dict untuk banyak URL paralel.

    Args:
        urls: daftar URL.
        analyzer: callable(response, soup) -> dict hasil.
        workers: jumlah thread (bounded, tetap rate-limited oleh session).
        progress: tampilkan progres sederhana.

    Returns:
        List of dict hasil + kolom url/status/error per entri.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def worker(url: str) -> Dict:
        try:
            response = fetch_page(url)
            soup = parse_soup(response.content)
            result = analyzer(response, soup)
            result.setdefault("url", response.url)
            result.setdefault("status", response.status_code)
            result.setdefault("error", "")
            return result
        except Exception as e:
            return {"url": url, "status": "", "error": str(e)}

    results: List[Dict] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(worker, u): u for u in urls}
        for i, future in enumerate(as_completed(futures), 1):
            results.append(future.result())
            if progress and i % 10 == 0:
                print(f"  ... {i}/{len(futures)} URL", end="\r")
    if progress:
        print(" " * 30, end="\r")
    return results


def _title_meta_analyzer(response, soup):
    """Analyzer batch: title/meta/canonical."""
    from ..analyzer.meta import extract_page_meta

    meta = extract_page_meta(response.url)
    return {
        "title": meta["title"] or "",
        "meta_description": meta["meta_description"] or "",
        "canonical": meta["canonical"] or "",
    }


def _headings_analyzer(response, soup):
    """Analyzer batch: ringkasan heading."""
    from ..analyzer.headings import analyze_headings

    result = analyze_headings(soup)
    return {
        "h1_count": result["h1_count"],
        "heading_count": len(result["headings"]),
        "skipped_levels": len(result["skipped_levels"]),
    }


BATCH_ANALYZERS = {"1": _title_meta_analyzer, "2": _headings_analyzer}


def export_interactive() -> None:
    """Menu interaktif: analisis batch banyak URL -> export CSV/JSON/HTML."""
    print("===== Export CSV/JSON/HTML + Batch Mode =====")
    print("Masukkan URL satu per satu (kosong + Enter untuk selesai):")
    urls: List[str] = []
    while True:
        try:
            url = input("URL (atau kosong): ").strip()
        except EOFError:
            break
        if not url:
            break
        urls.append(url)

    if not urls:
        print(colorize("Tidak ada URL yang dimasukkan.", "red"))
        return

    print("\nPilih analisis: 1=Title/Meta/Canonical, 2=Headings ringkas")
    choice = input("Pilihan (default 1): ").strip() or "1"
    analyzer = BATCH_ANALYZERS.get(choice)
    if analyzer is None:
        print(colorize("Pilihan analisis tidak valid.", "red"))
        return

    print(f"\nMenganalisis {len(urls)} URL (paralel, rate-limited)...")
    rows = batch_analyze(urls, analyzer)

    fmt = ""
    while fmt not in ("csv", "json", "html"):
        fmt = input("Format export (csv/json/html): ").strip().lower()
    output = input("Nama file output (default: laporan): ").strip() or "laporan"

    try:
        path = export_rows(rows, output, fmt)
    except ValueError as e:
        print(colorize(str(e), "red"))
        return
    print(colorize(f"\n{len(rows)} baris diekspor ke {path}", "green"))
