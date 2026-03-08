#!/usr/bin/env python3
"""Convert the repository CORAS SVG icons into PDF assets for the LaTeX package."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    default_source = repo_root / "tex" / "latex" / "corasdiagram" / "icons-src"
    default_dest = repo_root / "tex" / "latex" / "corasdiagram" / "icons"

    parser = argparse.ArgumentParser(
        description="Build PDF icon assets for the corasdiagram LaTeX package."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=default_source,
        help=f"Directory containing the CORAS SVG icons (default: {default_source})",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=default_dest,
        help=f"Destination directory for generated PDF icons (default: {default_dest})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.expanduser().resolve()
    dest = args.dest.expanduser().resolve()

    try:
        import cairosvg
    except ImportError as exc:
        print(
            "cairosvg is required. Install it with `pip3 install cairosvg` and rerun.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)
        return 1

    if not source.exists():
        print(f"Source directory not found: {source}", file=sys.stderr)
        return 1

    dest.mkdir(parents=True, exist_ok=True)
    converted = 0

    for svg_path in sorted(source.glob("*.svg")):
        pdf_path = dest / f"{svg_path.stem}.pdf"
        svg_text = svg_path.read_text(encoding="utf-8")
        svg_text = re.sub(r"<!DOCTYPE svg PUBLIC.*?\]>\s*", "", svg_text, flags=re.S)
        svg_text = svg_text.replace(
            'xmlns="&amp;ns_svg;"', 'xmlns="http://www.w3.org/2000/svg"'
        )
        svg_text = svg_text.replace(
            'xmlns:xlink="&amp;ns_xlink;"',
            'xmlns:xlink="http://www.w3.org/1999/xlink"',
        )
        svg_text = svg_text.replace(
            'xmlns="&ns_svg;"', 'xmlns="http://www.w3.org/2000/svg"'
        )
        svg_text = svg_text.replace(
            'xmlns:xlink="&ns_xlink;"',
            'xmlns:xlink="http://www.w3.org/1999/xlink"',
        )
        cairosvg.svg2pdf(bytestring=svg_text.encode("utf-8"), write_to=str(pdf_path))
        converted += 1
        print(f"wrote {pdf_path}")

    if converted == 0:
        print(f"No SVG files found in {source}", file=sys.stderr)
        return 1

    print(f"Converted {converted} icons into {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
