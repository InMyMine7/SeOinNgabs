## SeOinNgabs
<img src="https://raw.githubusercontent.com/InMyMine7/MineSeven/main/Seo.png">

CLI tool SEO berbasis Python 3. Semua request memakai timeout, User-Agent jelas, retry terbatas, dan rate limit.

# Tools Features
<ul>
    <li>Google Trends Scrapper</li>
    <li>Keyword Research</li>
    <li>Backlink Generator</li>
    <li>Check Status Url</li>
    <li>Check Title, Meta, URL Canonical</li>
    <li>h1, h2, h3, h4, h5, h6 checker</li>
    <li>Check backlink internal dan external beserta anchor text</li>
    <li>Check Broken Links</li>
    <li>Analisa link 403 dan 301</li>
    <li>Analisis Kecepatan Muat Gambar di Halaman</li>
    <li>Keyword Density Checker Tool</li>
    <li>.htaccess File Generator Tool</li>
    <li>Robots.txt Generator Tool</li>
    <li>Meta Tag Generator</li>
    <li>Terms Of Services Generator Tool</li>
    <li>Privacy Policy Generator Tool</li>
    <li>Disclaimer Generator Tool</li>
    <li>Open Graph / Twitter Card Checker</li>
    <li>Image Alt Checker</li>
    <li>Title & Meta Length Checker + SERP Preview</li>
    <li>Redirect Chain Tracer</li>
    <li>Site Crawler</li>
    <li>Sitemap Generator & Validator</li>
    <li>Schema.org JSON-LD Generator</li>
    <li>Export CSV/JSON/HTML + Batch Mode</li>
</ul>

## Installation

```bash
pip install -r requirements.txt
python main.py
```

> Catatan: proyek ini membutuhkan Python 3.8+. Di Windows, jika `python` masih menunjuk ke Python 2, gunakan `py -3 main.py`.

## Project Structure

```
seoinngabs/
├── cli/          # Menu interaktif + banner
├── core/         # HTTP session (timeout/UA/retry/rate limit), URL utils, output
├── research/     # Google Trends (RSS), keyword research
├── analyzer/     # Meta, headings, links, broken, redirects, images, density
├── generators/   # .htaccess, robots.txt, meta tags, dokumen legal
└── data/         # backlink.json (3000 situs)
tests/            # Test suite (pytest)
```

## Testing

```bash
pip install pytest responses
pytest tests/ -q
```
