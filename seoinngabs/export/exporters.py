"""Export analysis results to CSV / JSON / HTML + batch mode."""

import csv
import html
import io
import json
from pathlib import Path
from typing import Callable, Dict, List

from ..analyzer.fetch import fetch_page, parse_soup
from ..core.ui import ask, fail, header, paint, success, warn


def rows_to_csv(rows: List[Dict]) -> str:
    """Render a list of dicts as CSV (union of columns)."""
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
    """Render a list of dicts as indented JSON."""
    return json.dumps(rows, indent=2, ensure_ascii=False, default=str)


def rows_to_html(rows: List[Dict], title: str = "Report") -> str:
    """Render a list of dicts as an HTML table."""
    fieldnames: List[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    esc = html.escape
    parts = [f"<html><head><meta charset='utf-8'><title>{esc(title)}</title></head><body>"]
    parts.append(f"<h1>{esc(title)}</h1>")
    parts.append(f"<p>{len(rows)} rows</p>")
    parts.append("<table border='1' cellpadding='4' cellspacing='0'>")
    parts.append("<tr>" + "".join(f"<th>{esc(str(f))}</th>" for f in fieldnames) + "</tr>")
    for row in rows:
        cells = "".join(f"<td>{esc(_to_cell(row.get(f)))}</td>" for f in fieldnames)
        parts.append(f"<tr>{cells}</tr>")
    parts.append("</table></body></html>")
    return "\n".join(parts)


def export_rows(rows: List[Dict], output_path: str, fmt: str = "csv") -> Path:
    """Save rows to a file in the chosen format.

    Raises:
        ValueError: unknown format.
    """
    fmt = fmt.lower().lstrip(".")
    if fmt not in ("csv", "json", "html"):
        raise ValueError(f"Unsupported format: {fmt!r} (choose csv/json/html)")

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
    """Convert a cell value into a CSV/HTML-safe string."""
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
    """Run analyzer(response, soup) -> dict for many URLs in parallel."""
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
                print(f"  ... {i}/{len(futures)} URLs", end="\r")
    if progress:
        print(" " * 30, end="\r")
    return results


def _title_meta_analyzer(response, soup):
    """Batch analyzer: title/meta/canonical."""
    from ..analyzer.meta import extract_page_meta

    meta = extract_page_meta(response.url)
    return {
        "title": meta["title"] or "",
        "meta_description": meta["meta_description"] or "",
        "canonical": meta["canonical"] or "",
    }


def _headings_analyzer(response, soup):
    """Batch analyzer: heading summary."""
    from ..analyzer.headings import analyze_headings

    result = analyze_headings(soup)
    return {
        "h1_count": result["h1_count"],
        "heading_count": len(result["headings"]),
        "skipped_levels": len(result["skipped_levels"]),
    }


BATCH_ANALYZERS = {"1": _title_meta_analyzer, "2": _headings_analyzer}


def export_interactive() -> None:
    """Interactive: batch-analyze many URLs, then export as CSV/JSON/HTML."""
    print(header("Export CSV/JSON/HTML", "Batch analysis and reporting"))
    print(paint("  Enter URLs one per line (empty line to finish):", ""))
    urls: List[str] = []
    while True:
        try:
            url = input("    URL: ").strip()
        except EOFError:
            break
        if not url:
            break
        urls.append(url)

    if not urls:
        print(fail("No URLs entered."))
        return

    print("\n  Choose an analysis:")
    print("    1  Title / Meta / Canonical")
    print("    2  Headings summary")
    choice = ask("Analysis", "1")
    analyzer = BATCH_ANALYZERS.get(choice)
    if analyzer is None:
        print(fail("Invalid analysis choice."))
        return

    print(f"\n  Analyzing {len(urls)} URLs (parallel, rate-limited)...")
    rows = batch_analyze(urls, analyzer)

    fmt = ""
    while fmt not in ("csv", "json", "html"):
        fmt = ask("Export format (csv/json/html)", "csv").lower()
    output = ask("Output file name", "report")

    try:
        path = export_rows(rows, output, fmt)
    except ValueError as e:
        print(fail(str(e)))
        return
    print(success(f"{len(rows)} rows exported to {path}"))
