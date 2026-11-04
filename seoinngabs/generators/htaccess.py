"""Generator .htaccess with input validation."""

import re
from pathlib import Path

from ..core.ui import ask, confirm_overwrite, fail, header, success, warn
from ..core.url import is_valid_domain

PATH_RE = re.compile(r"^/[A-Za-z0-9._~!$&'()*+,;=:@%/-]*$")


def validate_htaccess_path(value: str) -> bool:
    """True when a path is safe for an Apache directive."""
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
    """Assemble .htaccess content from options (RewriteEngine written once)."""
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


def generate_htaccess() -> None:
    """Interactive: build and save .htaccess."""
    print(header(".htaccess Generator", "Apache configuration snippets"))

    https_redirect = ask("Redirect HTTP to HTTPS? (y/n)", "n").lower() == "y"

    error_page = ""
    if ask("Set a custom 404 error page? (y/n)", "n").lower() == "y":
        error_page = ask("Path for the 404 page (e.g. /404.html)")
        while not validate_htaccess_path(error_page):
            print(fail("Invalid path — must start with '/' and contain no quotes."))
            error_page = ask("Path for the 404 page")

    cache_control = ask("Set cache-control headers for static files? (y/n)", "n").lower() == "y"
    disable_dir_listing = ask("Disable directory listing? (y/n)", "n").lower() == "y"
    gzip = ask("Enable GZIP compression? (y/n)", "n").lower() == "y"

    redirects = []
    if ask("Add custom redirects? (y/n)", "n").lower() == "y":
        while True:
            source = ask("Source path (e.g. /old-page)")
            destination = ask("Destination path (e.g. /new-page)")
            if validate_htaccess_path(source) and validate_htaccess_path(destination):
                redirects.append((source, destination))
            else:
                print(fail("Invalid path — must start with '/'."))
            if ask("Add another redirect? (y/n)", "n").lower() != "y":
                break

    hotlink_domain = ""
    if ask("Prevent image hotlinking? (y/n)", "n").lower() == "y":
        hotlink_domain = ask("Your domain (e.g. example.com)")
        while not is_valid_domain(hotlink_domain):
            print(fail("Invalid domain."))
            hotlink_domain = ask("Your domain")

    output_path = Path.cwd() / ".htaccess"
    if not confirm_overwrite(str(output_path)):
        return
    if output_path.exists():
        output_path.rename(output_path.with_name(".htaccess.bak"))

    content = build_htaccess(
        https_redirect=https_redirect,
        error_page=error_page,
        cache_control=cache_control,
        disable_dir_listing=disable_dir_listing,
        gzip=gzip,
        redirects=redirects,
        hotlink_domain=hotlink_domain,
    )
    output_path.write_text(content, encoding="utf-8")
    print(success(f".htaccess written to {output_path}"))
