#!/usr/bin/env python3
"""Local browser-based anchor editor for corasdiagram symbol anchors.

The editor writes directly to the canonical symbol anchor tables in
tex/latex/corasdiagram/corasdiagram.sty. It is a tuning tool for editable
anchor maps, not a replacement for the visual regression fixtures or normal
package verification.
"""

from __future__ import annotations

import argparse
import json
import math
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
import webbrowser
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_PATH = REPO_ROOT / "tex" / "latex" / "corasdiagram" / "corasdiagram.sty"
ICONS_SRC_DIR = REPO_ROOT / "assets" / "icons-src"
STATIC_DIR = REPO_ROOT / "tools" / "coras_anchor_editor_web"
GENERATED_DIR = REPO_ROOT / "build" / "coras-anchor-editor"
PREVIEW_FIXTURE = REPO_ROOT / "tests" / "corasdiagram" / "icon-anchor-regression.tex"
ROUND_STEP_MM = 0.05
GRID_EXTENTS = {"xmin": -40, "xmax": 40, "ymin": -28, "ymax": 28, "minor_step": 1, "major_step": 5}
ANCHOR_ORDER = (
    "northwest",
    "north",
    "northeast",
    "west",
    "east",
    "southwest",
    "south",
    "southeast",
)
ANCHOR_TAILS = {
    "northwest": (-22.0, 19.0),
    "north": (0.0, 26.0),
    "northeast": (22.0, 19.0),
    "west": (-28.0, 4.0),
    "east": (28.0, 4.0),
    "southwest": (-22.0, -19.0),
    "south": (0.0, -26.0),
    "southeast": (22.0, -19.0),
}
PREVIEW_IMAGES = (
    {
        "id": "scenario-treatment",
        "title": "Scenario and Treatment (read-only)",
        "page": 3,
        "filename": "icon-anchor-regression-p3.png",
        "description": "Preview-only body-shape nodes that still use the LaTeX body anchor model.",
    },
    {
        "id": "incident-risk",
        "title": "Incident and Risk (read-only)",
        "page": 4,
        "filename": "icon-anchor-regression-p4.png",
        "description": "Read-only preview of rectangle-based body nodes and mounted icons.",
    },
)


@dataclass(frozen=True)
class SymbolConfig:
    symbol: str
    label: str
    icon_file: str
    icon_width_mm: float


EDITABLE_SYMBOLS = (
    SymbolConfig("asset", "Asset", "asset.svg", 10.0),
    SymbolConfig("indirectasset", "Indirect asset", "indirect-asset.svg", 10.0),
    SymbolConfig("stakeholder", "Stakeholder", "stakeholder.svg", 7.0),
    SymbolConfig("threataccidental", "Threat: accidental", "threat-human-accidental.svg", 10.0),
    SymbolConfig("threatdeliberate", "Threat: deliberate", "threat-human-deliberate.svg", 10.0),
    SymbolConfig("threatnonhuman", "Threat: non-human", "threat-non-human.svg", 13.0),
    SymbolConfig("vulnerability", "Vulnerability", "vulnerability.svg", 8.0),
)

EDITABLE_SYMBOL_MAP = {config.symbol: config for config in EDITABLE_SYMBOLS}
DISPLAY_ANCHOR_NAMES = {
    "northwest": "north west",
    "north": "north",
    "northeast": "north east",
    "west": "west",
    "east": "east",
    "southwest": "south west",
    "south": "south",
    "southeast": "south east",
}

METRIC_LINE_RE = re.compile(
    r"(?P<indent>\s*)\\corasdiagram@setsymbolmetric\{(?P<symbol>[a-z]+)\}\{(?P<metric>[a-z]+)\}\{(?P<value>[^}]+)\}\%"
)
ANCHOR_LINE_RE = re.compile(
    r"(?P<indent>\s*)\\corasdiagram@setsymbolanchor\{(?P<symbol>[a-z]+)\}\{(?P<anchor>[a-z]+)\}\{(?P<x>[^}]+)\}\{(?P<y>[^}]+)\}\%"
)
SVG_DOCTYPE_WITH_SUBSET_RE = re.compile(r"<!DOCTYPE\s+svg\b[\s\S]*?\]>", re.IGNORECASE)
SVG_DOCTYPE_SIMPLE_RE = re.compile(r"<!DOCTYPE\s+svg\b[^>]*>", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local CORAS anchor editor.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=8765, help="Bind port. Default: 8765")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not auto-open the browser after starting the server.",
    )
    return parser.parse_args()


def parse_mm_value(raw: str) -> float:
    raw = raw.strip()
    if not raw.endswith("mm"):
        raise ValueError(f"Expected millimeter value, got `{raw}`")
    return float(raw[:-2])


def round_mm_value(value: float) -> float:
    rounded = round(value / ROUND_STEP_MM) * ROUND_STEP_MM
    if math.isclose(rounded, 0.0, abs_tol=ROUND_STEP_MM / 2):
        return 0.0
    return rounded


def format_mm_value(value: float) -> str:
    rounded = round_mm_value(value)
    text = f"{rounded:.2f}".rstrip("0").rstrip(".")
    if text in {"-0", ""}:
        text = "0"
    return f"{text}mm"


def mm_values_match(existing: str, candidate: float) -> bool:
    return math.isclose(parse_mm_value(existing), round_mm_value(candidate), abs_tol=1e-9)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sanitize_svg_for_browser(text: str) -> str:
    sanitized = SVG_DOCTYPE_WITH_SUBSET_RE.sub("", text)
    sanitized = SVG_DOCTYPE_SIMPLE_RE.sub("", sanitized)
    sanitized = sanitized.replace('xmlns="&amp;ns_svg;"', 'xmlns="http://www.w3.org/2000/svg"')
    sanitized = sanitized.replace('xmlns="&ns_svg;"', 'xmlns="http://www.w3.org/2000/svg"')
    sanitized = sanitized.replace(
        'xmlns:xlink="&amp;ns_xlink;"',
        'xmlns:xlink="http://www.w3.org/1999/xlink"',
    )
    sanitized = sanitized.replace(
        'xmlns:xlink="&ns_xlink;"',
        'xmlns:xlink="http://www.w3.org/1999/xlink"',
    )
    return sanitized


def find_symbol_block(text: str, symbol: str) -> tuple[int, int, int, int]:
    start_re = re.compile(
        rf"\\newcommand\{{\\corasdiagram@defineanchors@{re.escape(symbol)}\}}\{{\%",
        re.MULTILINE,
    )
    start_match = start_re.search(text)
    if start_match is None:
        raise ValueError(f"Could not find anchor block for symbol `{symbol}`")
    body_start = start_match.end()
    end_re = re.compile(r"^}\s*$", re.MULTILINE)
    end_match = end_re.search(text, body_start)
    if end_match is None:
        raise ValueError(f"Could not find end of anchor block for symbol `{symbol}`")
    return start_match.start(), body_start, end_match.start(), end_match.end()


def parse_svg_aspect_ratio(path: Path) -> float:
    root = ET.fromstring(sanitize_svg_for_browser(read_text(path)))
    view_box = root.attrib.get("viewBox")
    if view_box:
        parts = [float(part) for part in view_box.replace(",", " ").split()]
        if len(parts) == 4 and parts[2] != 0:
            return parts[3] / parts[2]
    width = root.attrib.get("width")
    height = root.attrib.get("height")
    if width and height:
        width_value = float(re.sub(r"[^0-9.\-]+", "", width))
        height_value = float(re.sub(r"[^0-9.\-]+", "", height))
        if width_value != 0:
            return height_value / width_value
    return 1.0


def parse_package_symbols(package_path: Path) -> dict[str, dict[str, Any]]:
    text = read_text(package_path)
    data: dict[str, dict[str, Any]] = {}
    for config in EDITABLE_SYMBOLS:
        _, body_start, body_end, _ = find_symbol_block(text, config.symbol)
        body = text[body_start:body_end]
        metrics: dict[str, float] = {}
        anchors: dict[str, dict[str, float]] = {}
        for line in body.splitlines():
            metric_match = METRIC_LINE_RE.fullmatch(line)
            if metric_match and metric_match.group("symbol") == config.symbol:
                metrics[metric_match.group("metric")] = parse_mm_value(metric_match.group("value"))
                continue
            anchor_match = ANCHOR_LINE_RE.fullmatch(line)
            if anchor_match and anchor_match.group("symbol") == config.symbol:
                anchor_id = anchor_match.group("anchor")
                if anchor_id in ANCHOR_ORDER:
                    anchors[anchor_id] = {
                        "x": parse_mm_value(anchor_match.group("x")),
                        "y": parse_mm_value(anchor_match.group("y")),
                    }
        missing = [anchor for anchor in ANCHOR_ORDER if anchor not in anchors]
        if missing:
            raise ValueError(f"Missing anchors for symbol `{config.symbol}`: {', '.join(missing)}")
        svg_path = ICONS_SRC_DIR / config.icon_file
        data[config.symbol] = {
            "id": config.symbol,
            "label": config.label,
            "iconUrl": f"/icons/{config.icon_file}",
            "iconWidthMm": config.icon_width_mm,
            "iconAspectRatio": parse_svg_aspect_ratio(svg_path),
            "anchors": anchors,
            "metrics": metrics,
        }
    return data


def apply_anchor_updates(text: str, updates: dict[str, dict[str, dict[str, float]]]) -> str:
    updated_text = text
    for symbol in EDITABLE_SYMBOL_MAP:
        symbol_updates = updates.get(symbol)
        if not symbol_updates:
            continue
        _, body_start, body_end, _ = find_symbol_block(updated_text, symbol)
        body = updated_text[body_start:body_end]

        def replace_anchor(match: re.Match[str]) -> str:
            if match.group("symbol") != symbol:
                return match.group(0)
            anchor_name = match.group("anchor")
            if symbol_updates and anchor_name not in symbol_updates:
                return match.group(0)
            x_candidate = float(symbol_updates[anchor_name]["x"]) if symbol_updates else parse_mm_value(match.group("x"))
            y_candidate = float(symbol_updates[anchor_name]["y"]) if symbol_updates else parse_mm_value(match.group("y"))
            if mm_values_match(match.group("x"), x_candidate) and mm_values_match(
                match.group("y"), y_candidate
            ):
                return match.group(0)
            x_value = format_mm_value(x_candidate)
            y_value = format_mm_value(y_candidate)
            return (
                f"{match.group('indent')}\\corasdiagram@setsymbolanchor"
                f"{{{symbol}}}{{{anchor_name}}}{{{x_value}}}{{{y_value}}}%"
            )

        new_body = ANCHOR_LINE_RE.sub(replace_anchor, body)
        updated_text = updated_text[:body_start] + new_body + updated_text[body_end:]
    return updated_text


def save_anchor_updates(package_path: Path, updates: dict[str, dict[str, dict[str, float]]]) -> dict[str, Any]:
    original_text = read_text(package_path)
    new_text = apply_anchor_updates(original_text, updates)
    backup_path = package_path.with_suffix(package_path.suffix + ".bak")
    backup_path.write_text(original_text, encoding="utf-8")
    temp_path = package_path.with_suffix(package_path.suffix + ".tmp")
    temp_path.write_text(new_text, encoding="utf-8")
    os.replace(temp_path, package_path)
    return {
        "backupPath": str(backup_path),
        "packagePath": str(package_path),
        "changed": new_text != original_text,
        "symbols": parse_package_symbols(package_path),
    }


def ensure_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required tool `{name}` is not available on PATH")


def rebuild_preview_images() -> list[dict[str, str]]:
    ensure_tool("pdflatex")
    ensure_tool("pdftoppm")
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    preview_dir = GENERATED_DIR / "body-previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="coras-anchor-editor-") as temp_dir:
        temp_root = Path(temp_dir)
        env = os.environ.copy()
        env["TEXINPUTS"] = f"{REPO_ROOT / 'tex' / 'latex'}//:"
        env.setdefault("TEXMFVAR", str(temp_root / "texmf-var"))
        env.setdefault("TEXMFCACHE", env["TEXMFVAR"])
        output_dir = temp_root / "latex"
        output_dir.mkdir(parents=True, exist_ok=True)
        compile_result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={output_dir}",
                str(PREVIEW_FIXTURE),
            ],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(
                "Failed to compile icon-anchor-regression.tex\n"
                + compile_result.stdout
                + compile_result.stderr
            )
        pdf_path = output_dir / f"{PREVIEW_FIXTURE.stem}.pdf"
        raster_prefix = temp_root / "render" / "icon-anchor-regression"
        raster_prefix.parent.mkdir(parents=True, exist_ok=True)
        raster_result = subprocess.run(
            ["pdftoppm", "-r", "216", "-png", str(pdf_path), str(raster_prefix)],
            capture_output=True,
            text=True,
        )
        if raster_result.returncode != 0:
            raise RuntimeError(
                "Failed to rasterize icon-anchor-regression.pdf\n"
                + raster_result.stdout
                + raster_result.stderr
            )
        preview_entries: list[dict[str, str]] = []
        for preview in PREVIEW_IMAGES:
            raster_path = raster_prefix.parent / f"icon-anchor-regression-{preview['page']}.png"
            if not raster_path.exists():
                raise RuntimeError(f"Expected preview page `{raster_path.name}` was not created")
            destination = preview_dir / preview["filename"]
            shutil.copy2(raster_path, destination)
            preview_entries.append(
                {
                    "id": preview["id"],
                    "title": preview["title"],
                    "description": preview["description"],
                    "imageUrl": f"/generated/{destination.name}",
                }
            )
        return preview_entries


def previews_are_fresh() -> bool:
    preview_dir = GENERATED_DIR / "body-previews"
    if not preview_dir.exists():
        return False
    generated_paths = [preview_dir / preview["filename"] for preview in PREVIEW_IMAGES]
    if any(not path.exists() for path in generated_paths):
        return False
    freshness_target = max(PREVIEW_FIXTURE.stat().st_mtime, PACKAGE_PATH.stat().st_mtime)
    return all(path.stat().st_mtime >= freshness_target for path in generated_paths)


def get_preview_entries(force_rebuild: bool = False) -> tuple[list[dict[str, str]], str | None]:
    try:
        if force_rebuild or not previews_are_fresh():
            return rebuild_preview_images(), None
        preview_dir = GENERATED_DIR / "body-previews"
        return (
            [
                {
                    "id": preview["id"],
                    "title": preview["title"],
                    "description": preview["description"],
                    "imageUrl": f"/generated/{preview['filename']}",
                }
                for preview in PREVIEW_IMAGES
                if (preview_dir / preview["filename"]).exists()
            ],
            None,
        )
    except RuntimeError as exc:
        return [], str(exc)


def build_state(force_preview_rebuild: bool = False) -> dict[str, Any]:
    symbols = parse_package_symbols(PACKAGE_PATH)
    previews, preview_error = get_preview_entries(force_rebuild=force_preview_rebuild)
    return {
        "packagePath": str(PACKAGE_PATH),
        "symbols": [symbols[config.symbol] for config in EDITABLE_SYMBOLS],
        "anchorOrder": list(ANCHOR_ORDER),
        "anchorTails": {name: {"x": tail[0], "y": tail[1]} for name, tail in ANCHOR_TAILS.items()},
        "grid": GRID_EXTENTS,
        "previewOnlyNodes": ["scenario", "treatment", "incident", "risk"],
        "previews": previews,
        "previewError": preview_error,
    }


class AnchorEditorHandler(BaseHTTPRequestHandler):
    server_version = "CorasAnchorEditor/0.1"

    def log_message(self, fmt: str, *args: object) -> None: # type: ignore
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            return self._serve_static("index.html")
        if path in {"/app.js", "/styles.css"}:
            return self._serve_static(path.lstrip("/"))
        if path == "/api/state":
            return self._serve_json(HTTPStatus.OK, build_state())
        if path.startswith("/icons/"):
            return self._serve_file(ICONS_SRC_DIR / path.removeprefix("/icons/"))
        if path.startswith("/generated/"):
            return self._serve_file((GENERATED_DIR / "body-previews" / path.removeprefix("/generated/")))
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/save":
            return self._handle_save()
        if parsed.path == "/api/rebuild-preview":
            previews, error = get_preview_entries(force_rebuild=True)
            status = HTTPStatus.OK if error is None else HTTPStatus.INTERNAL_SERVER_ERROR
            return self._serve_json(status, {"previews": previews, "previewError": error})
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _read_json(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))

    def _handle_save(self) -> None:
        try:
            payload = self._read_json()
            updates = payload.get("symbols", {})
            if not isinstance(updates, dict):
                raise ValueError("Payload must contain a `symbols` object")
            normalized_updates: dict[str, dict[str, dict[str, float]]] = {}
            for symbol, anchors in updates.items():
                if symbol not in EDITABLE_SYMBOL_MAP:
                    continue
                if not isinstance(anchors, dict):
                    raise ValueError(f"Symbol `{symbol}` must map to an anchor object")
                normalized_updates[symbol] = {}
                for anchor_name, coords in anchors.items():
                    if anchor_name not in ANCHOR_ORDER:
                        continue
                    if not isinstance(coords, dict):
                        raise ValueError(f"Anchor `{anchor_name}` on `{symbol}` must be an object")
                    normalized_updates[symbol][anchor_name] = {
                        "x": float(coords["x"]),
                        "y": float(coords["y"]),
                    }
            result = save_anchor_updates(PACKAGE_PATH, normalized_updates)
            state = build_state()
            self._serve_json(
                HTTPStatus.OK,
                {
                    "message": "Saved anchor updates to corasdiagram.sty",
                    "backupPath": result["backupPath"],
                    "changed": result["changed"],
                    "state": state,
                },
            )
        except Exception as exc:  # pragma: no cover - exercised via integration
            self._serve_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    def _serve_static(self, name: str) -> None:
        self._serve_file(STATIC_DIR / name)

    def _serve_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        mime_type, _ = mimetypes.guess_type(path.name)
        if path.suffix == ".svg":
            mime_type = "image/svg+xml"
            data = sanitize_svg_for_browser(read_text(path)).encode("utf-8")
        else:
            data = path.read_bytes()
        if mime_type is None:
            mime_type = "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server(host: str, port: int, open_browser: bool) -> None:
    server = ThreadingHTTPServer((host, port), AnchorEditorHandler)
    url = f"http://{host}:{server.server_port}/"
    print(f"CORAS anchor editor listening at {url}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping CORAS anchor editor.")
    finally:
        server.server_close()


def main() -> int:
    args = parse_args()
    run_server(host=args.host, port=args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
