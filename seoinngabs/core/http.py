"""Layer HTTP terpusat: timeout, User-Agent, retry terbatas, rate limit."""

import time
from typing import Optional
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT: tuple = (10, 30)
USER_AGENT = "SeOinNgabs/2.0 (+https://github.com/InMyMine7/SeOinNgabs)"
MIN_REQUEST_INTERVAL = 0.5  # detik antar request ke host yang sama (rate limit)


class RateLimitedSession(requests.Session):
    """Session dengan interval minimal antar request per host."""

    def __init__(self, min_interval: float = MIN_REQUEST_INTERVAL) -> None:
        super().__init__()
        self._min_interval = min_interval
        self._last_request: dict = {}
        self.headers["User-Agent"] = USER_AGENT
        retry = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Request dengan rate limit per-host, timeout, dan UA default."""
        if "timeout" not in kwargs or kwargs["timeout"] is None:
            kwargs["timeout"] = DEFAULT_TIMEOUT
        host = urlparse(url).hostname or ""
        now = time.monotonic()
        last = self._last_request.get(host)
        if last is not None and (now - last) < self._min_interval:
            time.sleep(self._min_interval - (now - last))
        try:
            return super().request(method, url, **kwargs)
        finally:
            self._last_request[host] = time.monotonic()


_session: Optional[RateLimitedSession] = None


def get_session() -> RateLimitedSession:
    """Kembalikan session terpusat (dibuat lazy, thread-safe cukup untuk CLI)."""
    global _session
    if _session is None:
        _session = RateLimitedSession()
    return _session


def reset_session() -> None:
    """Tutup dan buat ulang session (untuk testing)."""
    global _session
    if _session is not None:
        _session.close()
    _session = None


def fetch_url(
    url: str,
    method: str = "GET",
    allow_redirects: Optional[bool] = None,
    **kwargs,
) -> requests.Response:
    """Wrapper request terpusat dengan fallback HEAD->GET tidak diperlukan di sini.

    Semua request fitur harus lewat sini agar timeout, UA, retry, dan rate
    limit konsisten (fix P1/P2/P3).
    """
    session = get_session()
    if allow_redirects is None:
        allow_redirects = method.upper() != "HEAD"
    return session.request(method.upper(), url, allow_redirects=allow_redirects, **kwargs)
