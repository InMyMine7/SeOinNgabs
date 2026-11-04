# SeOinNgabs

<img src="https://raw.githubusercontent.com/InMyMine7/MineSeven/main/Seo.png" alt="SeOinNgabs" align="left" width="96">

A Python 3 SEO toolkit for the command line — 27 tools covering keyword research, on-page analysis, link auditing, crawling, and file generation.

Every HTTP request runs with a timeout, a proper User-Agent, bounded retries, and per-host rate limiting. The site crawler respects `robots.txt`.

## Features

### Research
- **Google Trends Scraper** — daily trending searches for 30+ regions (or any custom geo code)
- **Keyword Research** — Google Suggest autocomplete in 20+ languages (or any custom `hl` code)

### On-Page Analysis
- **URL Status Checker** — response code + redirect info
- **Title, Meta & Canonical** — title, meta description, canonical URL (relative canonicals resolved), og:image
- **Heading Structure (h1–h6)** — hierarchy check: duplicate `<h1>`, level jumps (h1→h3), empty headings
- **Image Load Speed** — full-download timing and size per image, lazy-load (`data-src`, `srcset`) aware
- **Keyword Density** — word or phrase (1–3 gram) density with script/style text excluded

### Links & Backlinks
- **Backlink Generator** — submit your domain to 3,000 stat/whois sites (parallel, rate-limited)
- **Internal/External Links** — classification (www = apex), anchor text, `rel=nofollow`, dedup
- **Broken Links Checker** — parallel HEAD with GET fallback; 403/999 flagged for manual review
- **403/301 Redirect Analysis** — per-link status verification

### New Checkers
- **Open Graph / Twitter Card** — tag completeness + twitter:card validation
- **Image Alt Checker** — missing / empty / too-long alt text per image
- **Title & Meta Length + SERP Preview** — 60/160 char limits with a Google-style preview
- **Redirect Chain Tracer** — hop-by-hop trail with loop detection (max 10 hops)
- **HTTPS/SSL & Security Headers** — HTTP→HTTPS redirect, certificate expiry, 6 OWASP headers

### Crawling & Reporting
- **Site Crawler** — BFS crawl with depth/page limits, robots.txt respected, rate-limited
- **Sitemap Generator & Validator** — sitemaps.org XML, absolute-URL and W3C date validation
- **Export CSV/JSON/HTML + Batch Mode** — analyze many URLs in parallel, export as CSV, JSON, or HTML

### Generators
- **.htaccess Generator** — HTTPS redirect, 404 page, cache headers, GZIP, hotlink protection
- **robots.txt Generator** — grouped rules, crawl delay, sitemap location
- **Meta Tag Generator** — title/description/keywords + Open Graph + Twitter tags (HTML-escaped)
- **Terms of Service / Privacy Policy / Disclaimer** — templates with your inputs escaped and interpolated
- **Schema.org JSON-LD** — WebSite, Organization, Article, LocalBusiness, BreadcrumbList

## Installation

Requires Python 3.8+.

```bash
pip install -r requirements.txt
python main.py
```

> On Windows, if `python` still points to Python 2, run `py -3 main.py`.

## Usage

Interactive menu (all 27 tools):

```
python main.py
```

Or run a tool directly from the command line:

```bash
python main.py trends --geo US --limit 10
python main.py keywords "running shoes" --hl en
python main.py status https://example.com/
python main.py meta https://example.com/
python main.py headings https://example.com/
python main.py links https://example.com/
python main.py broken https://example.com/
python main.py redirects https://example.com/
python main.py trace https://example.com/old-page
python main.py images https://example.com/
python main.py density https://example.com/ "seo tools"
python main.py og https://example.com/
python main.py alt https://example.com/
python main.py serp https://example.com/
python main.py crawl https://example.com/ --depth 2 --max-pages 20
python main.py security https://example.com/
python main.py backlinks example.com
python main.py export https://a.com https://b.com --format csv --output report
```

See all commands and options:

```bash
python main.py --help
```

## Project Structure

```
seoinngabs/
├── cli/          # Interactive menu, banner, argparse CLI
├── core/         # HTTP session (timeout/UA/retry/rate limit), URL utils, UI helpers
├── research/     # Google Trends (RSS), keyword research
├── analyzer/     # meta, headings, links, broken, redirects, images, density,
│                 # og, alt, serp, redirect tracer, crawler, robots parser, security
├── generators/   # .htaccess, robots.txt, meta tags, sitemap, schema, legal docs
├── export/       # CSV/JSON/HTML exporters + batch mode
└── data/         # backlink.json (3,000 sites)
tests/            # Test suite (pytest + responses)
```

## Testing

```bash
pip install pytest responses
pytest tests/ -q
```

262 tests, all network calls mocked for deterministic runs.

## License

[WTFPL](LICENSE) — do what the f*ck you want.

---

Coded By '/Mine7 — [github.com/InMyMine7](https://github.com/InMyMine7) · [t.me/InMyMineee](https://t.me/InMyMineee)
