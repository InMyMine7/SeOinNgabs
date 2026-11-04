"""Generator .htaccess (fix L1-L4).

Perbaikan vs main.py lama:
- Semua input divalidasi (fix L1: tidak lagi bisa menghasilkan config invalid
  via injeksi karakter).
- Domain untuk hotlinking ditanya, bukan hardcoded yourdomain.com (fix L2).
- Konfirmasi sebelum menimpa + backup .htaccess.bak (fix L3).
- RewriteEngine On hanya ditulis sekali (fix L4).
"""

import re
from pathlib import Path

from ..core.output import colorize
from ..core.url import is_valid_domain

PATH_RE = re.compile(r"^/[A-Za-z0-9._~!$&'()*+,;=:@%/-]*$")
REDIRECT_PATH_RE = re.compile(r"^/[A-Za-z0-9._/-]*$")


def validate_htaccess_path(value: str) -> bool:
    """True bila path aman untuk directive Apache (fix L1)."""
    return bool(PATH_RE.match(value)) and '"' not in value and "\\" not in value and "\n" not in value


def build_htaccess(
    https_redirect: bool = False,
    error_page: str = "",
    cache_control: bool = False,
    disable_dir_listing: bool = False,
    gzip: bool = False,
    redirects: list = None,
    hotlink_domain: str = "",
) -> str:
    """Susun konten .htaccess dari opsi (fix L4: RewriteEngine sekali)."""
    content = []
    needs_rewrite = https_redirect or bool(hotlink_domain)
    if needs_rewrite:
        content.append("RewriteEngine On")
    if https_redirect:
        content.append("RewriteCond %{HTTPS} off")
        content.append("RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]")
    if error_page:
        content.append(f"ErrorDocument 404 {error_page}")
    if cache_control:
        content.append("# Cache control for static files")
        content.append('<FilesMatch "\\.(jpg|jpeg|png|gif|css|js|woff|woff2|ttf|svg|eot|ico)$">')
        content.append('Header set Cache-Control "max-age=31536000, public"')
        content.append("</FilesMatch>")
    if disable_dir_listing:
        content.append("Options -Indexes")
    if gzip:
        content.append("# Enable GZIP Compression")
        for mime in (
            "text/plain", "text/html", "text/xml", "text/css",
            "application/javascript", "application/x-javascript",
            "application/json", "application/xml",
        ):
            content.append(f"AddOutputFilterByType DEFLATE {mime}")
    for source, destination in redirects or []:
        content.append(f"Redirect 301 {source} {destination}")
    if hotlink_domain:
        content.append("# Prevent Hotlinking")
        content.append(f"RewriteCond %{{HTTP_REFERER}} !^https?://(www\\.)?{re.escape(hotlink_domain)} [NC]")
        content.append(r"RewriteRule \.(jpg|jpeg|png|gif|bmp|tiff|svg)$ - [F]")
    return "\n".join(content) + "\n"


def _confirm_overwrite(path: Path) -> bool:
    """Konfirmasi bila file output sudah ada (fix L3)."""
    if not path.exists():
        return True
    answer = input(f"{path.name} sudah ada. Timpa? (y/n): ").strip().lower()
    return answer == "y"


def generate_htaccess() -> None:
    """Menu interaktif: susun dan simpan .htaccess."""
    print(colorize("===== .htaccess File Generator =====", "green"))
    content_parts = {"redirects": []}

    print("\033[94m1. Redirect HTTP to HTTPS\033[0m")
    https_redirect = input("Do you want to redirect HTTP to HTTPS? (y/n): ").strip().lower() == "y"

    error_page = ""
    print("\033[94m2. Custom 404 Error Page\033[0m")
    if input("Do you want to set a custom 404 error page? (y/n): ").strip().lower() == "y":
        error_page = input("Enter the path for the custom 404 error page (e.g., /404.html): ").strip()
        while not validate_htaccess_path(error_page):
            print(colorize("Path tidak valid (harus diawali '/' tanpa kutip/karakter khusus).", "red"))
            error_page = input("Enter the path for the custom 404 error page: ").strip()
        content_parts["error_page"] = error_page

    print("\033[94m3. Set Cache Control Headers\033[0m")
    cache_control = input("Do you want to set cache control headers for static files? (y/n): ").strip().lower() == "y"

    print("\033[94m4. Disable Directory Listing\033[0m")
    disable_dir_listing = input("Do you want to disable directory listing? (y/n): ").strip().lower() == "y"

    print("\033[94m5. Enable GZIP Compression\033[0m")
    gzip = input("Do you want to enable GZIP compression? (y/n): ").strip().lower() == "y"

    redirects = []
    print("\033[94m6. Set Custom Redirects\033[0m")
    if input("Do you want to add custom redirects? (y/n): ").strip().lower() == "y":
        while True:
            source_url = input("Enter the source URL (e.g., /old-page): ").strip()
            destination_url = input("Enter the destination URL (e.g., /new-page): ").strip()
            if validate_htaccess_path(source_url) and validate_htaccess_path(destination_url):
                redirects.append((source_url, destination_url))
            else:
                print(colorize("Source/destination tidak valid (harus diawali '/').", "red"))
            if input("Do you want to add another redirect? (y/n): ").strip().lower() != "y":
                break

    hotlink_domain = ""
    print("\033[94m7. Prevent Hotlinking\033[0m")
    if input("Do you want to prevent hotlinking of images? (y/n): ").strip().lower() == "y":
        hotlink_domain = input("Enter your domain (e.g., example.com): ").strip()
        while not is_valid_domain(hotlink_domain):
            print(colorize("Domain tidak valid.", "red"))
            hotlink_domain = input("Enter your domain (e.g., example.com): ").strip()

    output_path = Path.cwd() / ".htaccess"
    if not _confirm_overwrite(output_path):
        return
    if output_path.exists():
        output_path.rename(output_path.with_name(".htaccess.bak"))

    content = build_htaccess(
        https_redirect=https_redirect,
        error_page=content_parts.get("error_page", ""),
        cache_control=cache_control,
        disable_dir_listing=disable_dir_listing,
        gzip=gzip,
        redirects=redirects,
        hotlink_domain=hotlink_domain,
    )
    output_path.write_text(content, encoding="utf-8")
    print(colorize(".htaccess file has been generated and saved.", "green"))
