#!/usr/bin/env python3
"""Entry point SeOinNgabs.

- Tanpa argumen: menu interaktif (perilaku lama).
- Dengan argumen: mode CLI (lihat `python main.py --help`).
"""

import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        from seoinngabs.cli.args import run_cli

        sys.exit(run_cli())
    from seoinngabs.cli.menu import run_menu

    run_menu()
