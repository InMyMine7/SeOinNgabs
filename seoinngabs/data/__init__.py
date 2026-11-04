"""Resolver path data — selalu absolut relatif terhadap package (fix C2, P4)."""

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DATA_DIR.parent.parent

BACKLINK_DB: Path = DATA_DIR / "backlink.json"


def data_path(name: str) -> Path:
    """Path absolut ke file data."""
    return DATA_DIR / name
