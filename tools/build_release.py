#!/usr/bin/env python3
"""Assemble a CTAN-friendly release bundle for corasdiagram."""

from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Build a CTAN-friendly release bundle for corasdiagram."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "dist",
        help="Directory for the generated bundle (default: dist/).",
    )
    parser.add_argument(
        "--doc-pdf",
        type=Path,
        help="Path to the generated manual PDF to include in the bundle.",
    )
    return parser.parse_args()


def read_version(package_file: Path) -> str:
    match = re.search(
        r"\\ProvidesPackage\{corasdiagram\}\[[^\]]* v([^\s]+) ",
        package_file.read_text(encoding="utf-8"),
    )
    if not match:
        raise RuntimeError(f"Could not determine version from {package_file}")
    return match.group(1)


def copy_tree(source: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)


def copy_example_sources(source_dir: Path, dest_dir: Path) -> None:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(source_dir.glob("*.tex")):
        shutil.copy2(path, dest_dir / path.name)


def resolve_artifact(repo_root: Path, path: Path) -> Path:
    candidates = []
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.append((Path.cwd() / path).resolve())
        candidates.append((repo_root / path).resolve())
        candidates.append((repo_root / path.name).resolve())

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists():
            return candidate

    raise RuntimeError(f"Documentation PDF not found: {path}")


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    package_file = repo_root / "tex" / "latex" / "corasdiagram" / "corasdiagram.sty"
    version = read_version(package_file)

    output_dir = args.output_dir.expanduser().resolve()
    bundle_root = output_dir / "ctan" / f"corasdiagram-{version}"
    doc_root = bundle_root / "doc" / "latex" / "corasdiagram"
    tex_root = bundle_root / "tex" / "latex" / "corasdiagram"

    output_dir.mkdir(parents=True, exist_ok=True)
    if bundle_root.exists():
        shutil.rmtree(bundle_root)

    doc_root.mkdir(parents=True, exist_ok=True)
    tex_root.parent.mkdir(parents=True, exist_ok=True)

    copy_tree(repo_root / "tex" / "latex" / "corasdiagram", tex_root)
    copy_example_sources(repo_root / "examples", doc_root / "examples")

    shutil.copy2(
        repo_root / "docs" / "corasdiagram-doc.tex",
        doc_root / "corasdiagram-doc.tex",
    )
    for filename in ("README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", "ROADMAP.md"):
        shutil.copy2(repo_root / filename, bundle_root / filename)

    doc_pdf = args.doc_pdf
    if doc_pdf is None:
        for candidate in (
            repo_root / "docs" / "corasdiagram-doc.pdf",
            repo_root / "corasdiagram-doc.pdf",
        ):
            if candidate.exists():
                doc_pdf = candidate
                break
    if doc_pdf is None:
        raise RuntimeError("Missing documentation PDF. Pass --doc-pdf after building docs.")

    doc_pdf = resolve_artifact(repo_root, doc_pdf.expanduser())

    shutil.copy2(doc_pdf, doc_root / "corasdiagram-doc.pdf")

    archive_path = output_dir / f"corasdiagram-{version}.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_root.parent))

    print(f"wrote {bundle_root}")
    print(f"wrote {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
