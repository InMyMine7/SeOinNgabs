"""HTTPS/SSL & security headers checker (Tahap 4 fitur #10).

Memeriksa:
- HTTPS: redirect HTTP -> HTTPS, HSTS
- SSL: sertifikat valid & belum expired (via socket, tanpa dependensi baru)
- Security headers (best practice OWASP):
  Strict-Transport-Security, Content-Security-Policy, X-Content-Type-Options,
  X-Frame-Options / frame-ancestors CSP, Referrer-Policy,
  Permissions-Policy, X-XSS-Protection (legacy)
"""

import socket
import ssl
import sys
from datetime import datetime, timezone
from typing import Dict, Optional
from urllib.parse import urlparse

from ..core.http import get_session
from ..core.output import colorize
from ..core.url import normalize_url

SECURITY_HEADERS = {
    "Strict-Transport-Security": "wajib bila HTTPS aktif (proteksi downgrade)",
    "Content-Security-Policy": "mitigasi XSS",
    "X-Content-Type-Options": "nosniff — cegah MIME sniffing",
    "X-Frame-Options": "clickjacking (atau CSP frame-ancestors)",
    "Referrer-Policy": "kontrol kebocoran referrer",
    "Permissions-Policy": "batasi API browser (kamera, lokasi, dst.)",
}


def _ssl_info(hostname: str, port: int = 443, timeout: float = 10.0) -> Dict:
    """Cek sertifikat SSL hostname. Tanpa dependensi tambahan."""
    result: Dict = {"valid": False, "error": None, "expires": None, "days_left": None, "issuer": None}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as tls:
                cert = tls.getpeercert()
        result["valid"] = True
        not_after = cert.get("notAfter")
        if not_after:
            expires = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            result["expires"] = expires.isoformat()
            result["days_left"] = (expires - datetime.now(timezone.utc)).days
        issuer = cert.get("issuer")
        if issuer:
            # issuer: tuple of tuples of (key, value)
            flat = [v for part in issuer for (_, v) in part if isinstance(part, tuple) and part]
            result["issuer"] = ", ".join(flat[:3]) or str(issuer)[:80]
    except (ssl.SSLError, socket.error, OSError, ValueError) as e:
        result["error"] = str(e)
    return result


def _headers_of(url: str) -> Dict[str, str]:
    """Ambil header respons (lowercase keys)."""
    session = get_session()
    response = session.get(url, allow_redirects=False, timeout=(10, 20))
    headers = {k.lower(): v for k, v in response.headers.items()}
    headers["__status__"] = str(response.status_code)
    response.close()
    return headers


def check_security(url: str) -> Dict:
    """Audit keamanan dasar sebuah URL.

    Returns:
        dict: https (bool), http_redirects_https (bool|None), ssl (dict),
        headers (dict header kecil), missing_headers (list), notes (list).
    """
    normalized = normalize_url(url)
    parsed = urlparse(normalized)
    hostname = parsed.hostname or ""
    report: Dict = {
        "url": normalized,
        "https": parsed.scheme == "https",
        "http_redirects_https": None,
        "ssl": None,
        "headers": {},
        "missing_headers": [],
        "notes": [],
    }

    # 1. Apakah http:// meredirect ke https://?
    if hostname:
        try:
            http_headers = _headers_of(f"http://{hostname}/")
            status = http_headers.get("__status__", "")
            location = http_headers.get("location", "")
            report["http_redirects_https"] = (
                status.startswith("3") and location.startswith("https://")
            )
            if status.startswith("2"):
                report["notes"].append("HTTP merespons 200 tanpa redirect ke HTTPS.")
        except Exception as e:
            report["notes"].append(f"HTTP check gagal: {e}")

    # 2. HTTPS + sertifikat
    if report["https"] or (report["http_redirects_https"] is True):
        report["ssl"] = _ssl_info(hostname)
        if report["ssl"]["error"]:
            report["notes"].append(f"SSL error: {report['ssl']['error']}")
        elif report["ssl"]["days_left"] is not None and report["ssl"]["days_left"] < 30:
            report["notes"].append(f"Sertifikat kedaluwarsa dalam {report['ssl']['days_left']} hari!")

    # 3. Security headers dari URL https (atau http bila https gagal)
    target = normalized if parsed.scheme == "https" else f"https://{hostname}/"
    try:
        headers = _headers_of(target)
        report["headers"] = {k: v for k, v in headers.items() if k != "__status__"}
        csp = headers.get("content-security-policy", "")
        xfo = headers.get("x-frame-options", "")
        for name, why in SECURITY_HEADERS.items():
            lower = name.lower()
            present = lower in headers
            if lower == "x-frame-options" and "frame-ancestors" in csp:
                present = True  # CSP frame-ancestors menggantikan XFO
            if lower == "strict-transport-security" and not report["https"]:
                if not (report["http_redirects_https"] or False):
                    report["missing_headers"].append(f"{name} — hanya relevan bila HTTPS aktif ({why})")
                continue
            if not present:
                report["missing_headers"].append(f"{name} — {why}")
        if report["https"] and "strict-transport-security" not in headers:
            report["missing_headers"].append("Strict-Transport-Security — wajib bila HTTPS aktif (proteksi downgrade)")
        report["headers"] = headers
        # hapus duplikat HSTS bila sudah ada
        report["missing_headers"] = list(dict.fromkeys(report["missing_headers"]))
    except Exception as e:
        report["notes"].append(f"Header check gagal: {e}")

    return report


def check_security_interactive() -> None:
    """Menu interaktif: audit HTTPS/SSL & security headers."""
    print("=====HTTPS/SSL & Security Headers Checker=====")
    url = input("\nMasukkan URL halaman: ").strip()
    try:
        report = check_security(url)
    except Exception as e:
        print("Terjadi kesalahan:", e)
        return

    print(f"\n{colorize('HTTPS:', 'green')} {'aktif' if report['https'] else 'TIDAK — situs belum HTTPS'}")
    if report["http_redirects_https"] is not None:
        state = "ya" if report["http_redirects_https"] else "TIDAK"
        print(f"HTTP -> HTTPS redirect: {state}")
    if report["ssl"]:
        ssl_info = report["ssl"]
        if ssl_info["valid"]:
            print(f"SSL: valid — kedaluwarsa {ssl_info['expires']} ({ssl_info['days_left']} hari lagi)")
        else:
            print(colorize(f"SSL: bermasalah — {ssl_info['error']}", "red"))
    print(f"\n{colorize('Security Headers:', 'green')}")
    for name, why in SECURITY_HEADERS.items():
        present = name.lower() in report["headers"] or (
            name == "X-Frame-Options" and "frame-ancestors" in report["headers"].get("content-security-policy", ""))
        mark = colorize("OK", "green") if present else colorize("MISSING", "red")
        print(f"  [{mark}] {name}")
    if report["missing_headers"]:
        print(f"\n{colorize('Rekomendasi:', 'red')}")
        for m in report["missing_headers"]:
            print(f"  - {m}")
    for note in report["notes"]:
        print(colorize(f"  [i] {note}", "red"))
