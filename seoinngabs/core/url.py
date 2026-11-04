"""Utilitas normalisasi dan validasi URL (fix D2, C4, J4)."""

import re
from urllib.parse import urljoin, urlparse

from .errors import InvalidURLError

SCHEME_RE = re.compile(r"^https?://", re.IGNORECASE)
DOMAIN_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)+$")


def normalize_url(user_input: str) -> str:
    """Normalisasi input URL dari pengguna.

    - Lowercase scheme (fix D2: 'HTTPS://X' tidak lagi menjadi 'http://HTTPS://X').
    - Tambah 'http://' bila scheme hilang.
    - Tolak input kosong / bukan http(s).

    Raises:
        InvalidURLError: bila input kosong atau scheme tidak didukung.
    """
    raw = (user_input or "").strip()
    if not raw:
        raise InvalidURLError("URL tidak boleh kosong.")
    if not SCHEME_RE.match(raw):
        raw = "http://" + raw
    parsed = urlparse(raw)
    if not parsed.netloc:
        raise InvalidURLError(f"URL tidak valid: {user_input!r}")
    # Lowercase scheme dan netloc, pertahankan path/query asli.
    return parsed._replace(scheme=parsed.scheme.lower()).geturl()


def is_valid_domain(domain: str) -> bool:
    """Validasi nama domain sederhana (fix C4)."""
    d = (domain or "").strip().lower().rstrip(".")
    return bool(d) and bool(DOMAIN_RE.match(d)) and len(d) <= 253 and ".." not in d


def join_url(base: str, href: str) -> str:
    """Gabung href relatif ke base dengan urljoin (fix G2, H1, J4).

    Menangani: relatif 'x.html', root-relative '/x', protocol-relative '//cdn',
    query-only '?q=1', dan absolute.
    """
    return urljoin(base, href)


def same_site(base_url: str, other_url: str, include_subdomains: bool = False) -> bool:
    """True bila other_url satu situs dengan base_url (fix G1).

    Membandingkan registrable host setelah normalisasi 'www.' (www dan apex
    dianggap sama). Bila include_subdomains=True, sub.example.com dianggap
    satu situs dengan example.com.
    """
    b = urlparse(base_url).hostname or ""
    o = urlparse(other_url).hostname or ""
    if not b or not o:
        return False
    b = b[4:] if b.startswith("www.") else b
    o = o[4:] if o.startswith("www.") else o
    if b == o:
        return True
    if include_subdomains and (o.endswith("." + b) or b.endswith("." + o)):
        return True
    return False
