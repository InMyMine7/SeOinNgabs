"""robots.txt parser sederhana (Tahap 4 fitur #5 — pendukung crawler).

Implementasi minimal aturan robots.txt yang relevan untuk crawler internal:
- User-agent grouping (termasuk '*')
- Disallow / Allow prefix matching (longest match menang, sesuai spesifikasi)
- Crawl-delay (diambil dari grup yang menang)
- Sitemap

Bukan pengganti library robotparser penuh, tapi menghormati aturan inti
Google/BERG. Untuk ketat-ke-standar, urllib.robotparser bisa dipakai; ini
dipilih agar delay dan debug info mudah diekstrak.
"""

from typing import Dict, List, Optional, Tuple

from ..core.http import get_session


class RobotsRule:
    """Satu grup aturan (User-agent + Allow/Disallow + Crawl-delay)."""

    def __init__(self, agents: List[str]) -> None:
        self.agents = [a.lower() for a in agents]
        self.allow: List[str] = []
        self.disallow: List[str] = []
        self.crawl_delay: Optional[float] = None


class RobotsTxt:
    """Hasil parse robots.txt."""

    def __init__(self) -> None:
        self.rules: List[RobotsRule] = []
        self.sitemaps: List[str] = []
        self.raw: str = ""

    def _matching_rules(self, user_agent: str) -> List[RobotsRule]:
        ua = user_agent.lower()
        # aturan spesifik agen menang atas '*'; gabungkan semua grup cocok
        specific = [r for r in self.rules if ua in r.agents]
        wildcard = [r for r in self.rules if "*" in r.agents]
        return specific or wildcard

    def is_allowed(self, path: str, user_agent: str = "*") -> bool:
        """True bila path boleh di-crawl oleh user_agent."""
        for rule in self._matching_rules(user_agent):
            # longest match menang antara allow dan disallow
            best_allow = max((len(p) for p in rule.allow if path.startswith(p)), default=-1)
            best_disallow = max((len(p) for p in rule.disallow if path.startswith(p)), default=-1)
            if best_disallow > best_allow:
                return False
            if best_allow >= 0 and best_disallow < 0:
                return True
        return True  # tidak ada aturan yang cocok -> boleh

    def get_crawl_delay(self, user_agent: str = "*") -> Optional[float]:
        """Crawl-delay dari grup aturan yang cocok (None bila tidak diset)."""
        for rule in self._matching_rules(user_agent):
            if rule.crawl_delay is not None:
                return rule.crawl_delay
        return None


def parse_robots_txt(content: str) -> RobotsTxt:
    """Parse isi robots.txt menjadi struktur aturan."""
    robots = RobotsTxt()
    robots.raw = content
    current: Optional[RobotsRule] = None
    current_agents: List[str] = []

    for raw_line in content.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, _, value = line.partition(":")
        field = field.strip().lower()
        value = value.strip()

        if field == "user-agent":
            if current is not None and current_agents != [value]:
                # grup baru dimulai bila agen berbeda dari baris sebelumnya
                current = None
            if current is None:
                current_agents = []
            current_agents.append(value)
        elif field in ("disallow", "allow"):
            if current is None:
                current = RobotsRule(current_agents or ["*"])
                robots.rules.append(current)
            # 'Disallow:' kosong = tidak ada larangan (spesifikasi robots.txt)
            if value:
                (current.disallow if field == "disallow" else current.allow).append(value)
        elif field == "crawl-delay":
            if current is None:
                current = RobotsRule(current_agents or ["*"])
                robots.rules.append(current)
            try:
                current.crawl_delay = float(value)
            except ValueError:
                pass
        elif field == "sitemap":
            robots.sitemaps.append(value)

    return robots


def fetch_robots_txt(base_url: str, user_agent: str = "*") -> RobotsTxt:
    """Fetch + parse robots.txt dari situs; situs tanpa robots = semua boleh."""
    from ..core.url import normalize_url
    from urllib.parse import urljoin

    base = normalize_url(base_url)
    robots_url = urljoin(base, "/robots.txt")
    try:
        response = get_session().get(robots_url, timeout=(10, 20))
        if response.status_code == 200:
            return parse_robots_txt(response.text)
    except Exception:
        pass
    return RobotsTxt()  # kosong = semua diizinkan
