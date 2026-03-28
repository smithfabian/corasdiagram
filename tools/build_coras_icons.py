#!/usr/bin/env python3
"""Build generated runtime icon assets from the canonical SVG sources.

The repository treats assets/icons-src/ as the editable icon source tree and
tex/latex/corasdiagram/icons/ as generated runtime assets used by the LaTeX
package. Run this script after intentional icon source changes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RUNTIME_ICON_PREFIX = "corasdiagram-"


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    default_source = repo_root / "assets" / "icons-src"
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


SVG_DOCTYPE_WITH_SUBSET_RE = re.compile(r"<!DOCTYPE\s+svg\b[\s\S]*?\]>", re.IGNORECASE)
SVG_DOCTYPE_SIMPLE_RE = re.compile(r"<!DOCTYPE\s+svg\b[^>]*>", re.IGNORECASE)
HEX_COLOR_RE = re.compile(r"#[0-9A-Fa-f]{3,6}")


def sanitize_svg_text(svg_text: str) -> str:
    svg_text = SVG_DOCTYPE_WITH_SUBSET_RE.sub("", svg_text)
    svg_text = SVG_DOCTYPE_SIMPLE_RE.sub("", svg_text)
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
    return svg_text


def to_grayscale_hex(color: str) -> str:
    color = color.strip()
    if len(color) == 4:
        color = "#" + "".join(ch * 2 for ch in color[1:])
    red = int(color[1:3], 16)
    green = int(color[3:5], 16)
    blue = int(color[5:7], 16)
    if red == green == blue:
        return f"#{red:02X}{green:02X}{blue:02X}"
    gray = round(0.299 * red + 0.587 * green + 0.114 * blue)
    return f"#{gray:02X}{gray:02X}{gray:02X}"


def derive_bw_svg_text(svg_text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        color = match.group(0)
        return to_grayscale_hex(color)

    return HEX_COLOR_RE.sub(replace, svg_text)


def runtime_pdf_path(dest: Path, stem: str) -> Path:
    return dest / f"{RUNTIME_ICON_PREFIX}{stem}.pdf"


def clear_managed_runtime_pdfs(dest: Path, source_stems: set[str]) -> None:
    """Delete only managed runtime PDFs from an existing output directory.

    This removes both the current prefixed filenames and the historical
    unprefixed names for known source stems, while leaving unrelated files in
    a user-supplied destination alone.
    """

    if not dest.exists():
        return
    if not dest.is_dir():
        raise ValueError(f"Destination path is not a directory: {dest}")

    managed_legacy_names = {f"{stem}.pdf" for stem in source_stems}
    for child in dest.iterdir():
        if not child.is_file() or child.suffix.lower() != ".pdf":
            continue
        if child.name.startswith(RUNTIME_ICON_PREFIX) or child.name in managed_legacy_names:
            child.unlink()


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

    base_svgs = sorted(
        svg_path for svg_path in source.glob("*.svg") if not svg_path.stem.endswith("_bw")
    )
    source_stems = {svg_path.stem for svg_path in base_svgs}
    source_stems.update(f"{svg_path.stem}_bw" for svg_path in base_svgs)

    clear_managed_runtime_pdfs(dest, source_stems)
    dest.mkdir(parents=True, exist_ok=True)
    converted = 0

    for svg_path in base_svgs:
        svg_text = sanitize_svg_text(svg_path.read_text(encoding="utf-8"))
        bw_svg_text = derive_bw_svg_text(svg_text)
        bw_svg_path = source / f"{svg_path.stem}_bw.svg"
        bw_svg_path.write_text(bw_svg_text, encoding="utf-8")

        pdf_path = runtime_pdf_path(dest, svg_path.stem)
        cairosvg.svg2pdf(bytestring=svg_text.encode("utf-8"), write_to=str(pdf_path))
        converted += 1
        print(f"wrote {pdf_path}")

        bw_pdf_path = runtime_pdf_path(dest, f"{svg_path.stem}_bw")
        cairosvg.svg2pdf(bytestring=bw_svg_text.encode("utf-8"), write_to=str(bw_pdf_path))
        converted += 1
        print(f"wrote {bw_pdf_path}")

    if converted == 0:
        print(f"No SVG files found in {source}", file=sys.stderr)
        return 1

    print(f"Converted {converted} icons into {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
