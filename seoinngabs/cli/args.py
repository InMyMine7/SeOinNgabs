"""Argumen CLI via argparse (Tahap 4 fitur #9) — alternatif menu interaktif.

Pemakaian:
    python main.py                          # menu interaktif (default)
    python main.py trends --geo ID
    python main.py keywords "sepatu lari"
    python main.py status https://example.com/
    python main.py meta https://example.com/
    python main.py headings https://example.com/
    python main.py links https://example.com/
    python main.py broken https://example.com/
    python main.py redirects https://example.com/old
    python main.py trace https://example.com/old
    python main.py images https://example.com/
    python main.py density https://example.com/ "kata kunci"
    python main.py og https://example.com/
    python main.py alt https://example.com/
    python main.py serp https://example.com/
    python main.py crawl https://example.com/ --depth 2 --max-pages 20
    python main.py backlinks example.com
    python main.py export u1 u2 --format csv --output laporan
    python main.py security https://example.com/
"""

import argparse
import json
import sys
from typing import List, Optional

from .. import __version__


def build_parser() -> argparse.ArgumentParser:
    """Susun parser CLI lengkap."""
    parser = argparse.ArgumentParser(
        prog="seoinngabs",
        description="SeOinNgabs — CLI tool SEO (mode argumen; tanpa argumen = menu interaktif).",
    )
    parser.add_argument("--version", action="version", version=f"SeOinNgabs {__version__}")

    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("trends", help="Google Trends trending searches")
    p.add_argument("--geo", default="ID", help="Kode negara (default: ID)")
    p.add_argument("--limit", type=int, default=20, help="Jumlah hasil maksimum")

    p = sub.add_parser("keywords", help="Riset keyword Google Suggest")
    p.add_argument("keyword", help="Kata kunci dasar")
    p.add_argument("--hl", default="id", help="Bahasa (default: id)")

    def url_arg(p):
        p.add_argument("url", help="URL halaman")

    p = sub.add_parser("status", help="Cek status URL")
    url_arg(p)

    p = sub.add_parser("meta", help="Title, meta description, canonical, og:image")
    url_arg(p)

    p = sub.add_parser("headings", help="Analisis heading h1-h6")
    url_arg(p)

    p = sub.add_parser("links", help="Link internal/eksternal + anchor")
    url_arg(p)

    p = sub.add_parser("broken", help="Broken link checker")
    url_arg(p)

    p = sub.add_parser("redirects", help="Analisis link 404/301/403")
    url_arg(p)

    p = sub.add_parser("trace", help="Redirect chain tracer")
    url_arg(p)

    p = sub.add_parser("images", help="Kecepatan muat gambar")
    url_arg(p)

    p = sub.add_parser("density", help="Keyword density")
    url_arg(p)
    p.add_argument("keyword", help="Kata kunci / frasa")

    p = sub.add_parser("og", help="Open Graph / Twitter Card checker")
    url_arg(p)

    p = sub.add_parser("alt", help="Image alt checker")
    url_arg(p)

    p = sub.add_parser("serp", help="Title/meta length + SERP preview")
    url_arg(p)

    p = sub.add_parser("crawl", help="Site crawler")
    url_arg(p)
    p.add_argument("--depth", type=int, default=2)
    p.add_argument("--max-pages", type=int, default=20)
    p.add_argument("--no-robots", action="store_true", help="Abaikan robots.txt (tidak disarankan)")

    p = sub.add_parser("backlinks", help="Backlink generator")
    p.add_argument("domain", help="Nama domain, mis. example.com")

    p = sub.add_parser("export", help="Batch analisis URL lalu export")
    p.add_argument("urls", nargs="+", help="Daftar URL")
    p.add_argument("--analysis", choices=["1", "2"], default="1",
                   help="1=title/meta/canonical, 2=headings ringkas")
    p.add_argument("--format", choices=["csv", "json", "html"], default="csv")
    p.add_argument("--output", default="laporan", help="Nama file output tanpa ekstensi")

    p = sub.add_parser("security", help="HTTPS/SSL & security headers checker")
    url_arg(p)

    return parser


def run_cli(argv: Optional[List[str]] = None) -> int:
    """Jalankan perintah CLI. Return exit code (0 sukses)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    from ..core.output import colorize

    try:
        if args.command == "trends":
            from ..research.trends import format_trends, get_trending_searches

            print(format_trends(get_trending_searches(geo=args.geo, limit=args.limit), geo=args.geo))
            return 0

        if args.command == "keywords":
            from ..research.keywords import research_keyword

            for suggestion in research_keyword(args.keyword, hl=args.hl):
                print(suggestion)
            return 0

        if args.command == "status":
            from ..analyzer.fetch import fetch_page

            response = fetch_page(args.url)
            print(f"Status: {response.status_code}")
            if response.history:
                print(f"URL asli: {response.history[0].url}")
                print(f"URL final: {response.url}")
            return 0

        if args.command == "meta":
            from ..analyzer.meta import extract_page_meta

            meta = extract_page_meta(args.url)
            for key in ("status", "base_url", "title", "meta_description", "canonical", "og_image"):
                print(f"{key}: {meta[key] or 'N/A'}")
            return 0

        if args.command == "headings":
            from ..analyzer.fetch import fetch_page, parse_soup
            from ..analyzer.headings import analyze_headings

            soup = parse_soup(fetch_page(args.url).content)
            result = analyze_headings(soup)
            for name, text in result["headings"]:
                print(f"{name}: {text or '(kosong)'}")
            print(f"h1_count: {result['h1_count']}, skipped: {len(result['skipped_levels'])}")
            return 0

        if args.command == "links":
            from ..analyzer.fetch import fetch_page, parse_soup
            from ..analyzer.links import classify_links

            response = fetch_page(args.url)
            result = classify_links(response.url, parse_soup(response.content))
            for kind in ("internal", "external"):
                print(f"--- {kind} ({len(result[kind])}) ---")
                for link in result[kind]:
                    nofollow = " [nofollow]" if link["nofollow"] else ""
                    print(f"{link['anchor'] or '(tanpa teks)'} -> {link['href']}{nofollow}")
            return 0

        if args.command == "broken":
            from ..analyzer.broken import collect_links
            from ..analyzer.fetch import fetch_page, parse_soup
            from ..analyzer.links import check_urls_parallel

            response = fetch_page(args.url)
            links = collect_links(response.url, parse_soup(response.content))
            for r in check_urls_parallel(links, progress=False):
                if r["error"]:
                    print(f"[ERROR] {r['url']}")
                elif r["status_code"] >= 400:
                    print(f"[BROKEN {r['status_code']}] {r['url']}")
            return 0

        if args.command == "redirects":
            from ..analyzer.fetch import fetch_page, parse_soup
            from ..analyzer.links import check_urls_parallel, classify_links

            response = fetch_page(args.url)
            result = classify_links(response.url, parse_soup(response.content))
            links = sorted({l["href"] for l in result["internal"] + result["external"]})
            for r in check_urls_parallel(links, progress=False):
                if r["status_code"] in (301, 302, 307, 308, 403, 404):
                    print(f"[{r['status_code']}] {r['url']}")
            return 0

        if args.command == "trace":
            from ..analyzer.redirect_tracer import trace_redirects

            result = trace_redirects(args.url)
            for i, hop in enumerate(result["hops"], 1):
                print(f"{i}. [{hop['status']}] {hop['url']}" + (f" -> {hop['location']}" if hop["location"] else ""))
            print(f"loop: {result['loop']}, completed: {result['completed']}")
            return 0

        if args.command == "images":
            from ..analyzer.fetch import fetch_page, parse_soup
            from ..analyzer.images import collect_image_urls, measure_image

            response = fetch_page(args.url)
            for img in collect_image_urls(parse_soup(response.content), response.url):
                r = measure_image(img)
                print(f"{r['url']}: {r['size']} bytes, {r['load_time']:.2f}s" if r["error"] is None
                      else f"{r['url']}: ERROR {r['error']}")
            return 0

        if args.command == "density":
            from ..analyzer.density import count_ngrams, extract_text, tokenize
            from ..analyzer.fetch import fetch_page, parse_soup

            soup = parse_soup(fetch_page(args.url).content)
            tokens = tokenize(extract_text(soup))
            n = len(args.keyword.split())
            freq = count_ngrams(tokens, args.keyword.lower(), n)
            total = len(tokens)
            print(f"{args.keyword}: {freq}/{total} = {freq / total * 100 if total else 0:.2f}%")
            return 0

        if args.command == "og":
            from ..analyzer.fetch import fetch_page, parse_soup
            from ..analyzer.og import analyze_og_twitter, og_twitter_recommendations

            soup = parse_soup(fetch_page(args.url).content)
            tags = analyze_og_twitter(soup)
            for name, value in tags.items():
                print(f"{'OK ' if value else 'MISS'} {name}: {value or '-'}")
            for rec in og_twitter_recommendations(tags):
                print(f"[!] {rec}")
            return 0

        if args.command == "alt":
            from ..analyzer.alt import analyze_image_alts
            from ..analyzer.fetch import fetch_page, parse_soup

            response = fetch_page(args.url)
            for r in analyze_image_alts(parse_soup(response.content), response.url):
                print(f"[{r['status'].upper()}] {r['url']} — alt: {r['alt']}")
            return 0

        if args.command == "serp":
            from ..analyzer.fetch import fetch_page, parse_soup
            from ..analyzer.serp import analyze_title_meta_lengths, render_serp_preview

            response = fetch_page(args.url)
            soup = parse_soup(response.content)
            result = analyze_title_meta_lengths(soup)
            print(f"title: {result['title']}")
            print(f"description: {result['description']}")
            print(render_serp_preview(
                result["title"]["value"] if result["title"] else None,
                response.url,
                result["description"]["value"] if result["description"] else None,
            ))
            return 0

        if args.command == "crawl":
            from ..analyzer.crawler import crawl_site

            for r in crawl_site(args.url, max_depth=args.depth, max_pages=args.max_pages,
                                respect_robots=not args.no_robots):
                print(f"[{r['status']}] {r['url']}" + (f" — {r['error']}" if r["error"] else ""))
            return 0

        if args.command == "backlinks":
            from urllib.parse import urlparse

            from ..analyzer.backlinks_gen import check_backlink_url, load_backlink_sites

            if not _valid_domain(args.domain):
                print(colorize(f"Domain tidak valid: {args.domain}", "red"))
                return 1
            for template in load_backlink_sites()[:50]:  # CLI: batasi 50 agar praktis
                url = template.replace("inmymine7", args.domain)
                r = check_backlink_url(url)
                domain = urlparse(url).netloc
                status = r["status"] if r["status"] is not None else f"ERROR ({r['error'][:40]})"
                print(f"{domain}: {status}")
            return 0

        if args.command == "export":
            from ..export.exporters import BATCH_ANALYZERS, batch_analyze, export_rows

            results = batch_analyze(args.urls, BATCH_ANALYZERS[args.analysis], progress=False)
            path = export_rows(results, args.output, args.format)
            print(f"{len(results)} baris -> {path}")
            return 0

        if args.command == "security":
            from ..analyzer.security import check_security

            report = check_security(args.url)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0

    except KeyboardInterrupt:
        print("\nDibatalkan.")
        return 130
    except Exception as e:
        print(colorize(f"Error: {e}", "red"), file=sys.stderr)
        return 1

    return 0


def _valid_domain(domain: str) -> bool:
    from ..core.url import is_valid_domain

    return is_valid_domain(domain)
