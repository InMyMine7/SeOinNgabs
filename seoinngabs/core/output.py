"""Helper output terminal: warna ANSI, clear screen, escape input untuk HTML."""

import html
import os
import sys

COLORS = {
    "h1": "\033[92m",
    "h2": "\033[93m",
    "h3": "\033[94m",
    "h4": "\033[95m",
    "h5": "\033[96m",
    "h6": "\033[91m",
    "green": "\033[92m",
    "red": "\033[91m",
    "reset": "\033[0m",
}


def supports_color() -> bool:
    """Deteksi apakah stdout adalah TTY (warna hanya jika terminal)."""
    try:
        return sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False


def colorize(text: str, color: str) -> str:
    """Bungkus teks dengan kode warna ANSI bila terminal mendukung."""
    if not supports_color():
        return text
    code = COLORS.get(color, COLORS["reset"])
    return f"{code}{text}{COLORS['reset']}"


def clear_screen() -> None:
    """Bersihkan layar terminal (cross-platform)."""
    os.system("cls" if os.name == "nt" else "clear")


def escape_html(value: str) -> str:
    """Escape input user untuk konten HTML (fix N1, O3)."""
    return html.escape(value, quote=True)
