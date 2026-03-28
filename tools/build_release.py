#!/usr/bin/env python3
"""Assemble the CTAN-friendly release bundle for corasdiagram.

Inputs come from the canonical repository sources: VERSION, the package tree,
the built manual PDF, examples, and repo-root metadata files. Contributors run
this locally to smoke-test the release contents before pushing a version tag.
"""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

from versioning import read_repo_version

RUNTIME_ICON_PREFIX = "corasdiagram-"

REQUIRED_BUNDLE_PATHS = (
    "assets/icons-src",
    "doc/corasdiagram-doc.pdf",
    "doc/corasdiagram-doc.tex",
    "doc/examples",
    "tex/corasdiagram-version.tex",
    "tex/corasdiagram.sty",
    "tex/icons",
)

FORBIDDEN_BUNDLE_PREFIXES = (
    "doc/latex",
    "tex/latex",
)

REQUIRED_ARCHIVE_FILES = (
    "corasdiagram/doc/corasdiagram-doc.pdf",
    "corasdiagram/doc/corasdiagram-doc.tex",
    "corasdiagram/tex/corasdiagram-version.tex",
    "corasdiagram/tex/corasdiagram.sty",
)

REQUIRED_ARCHIVE_PREFIXES = (
    "corasdiagram/assets/icons-src/",
    "corasdiagram/doc/examples/",
    "corasdiagram/tex/icons/",
)

FORBIDDEN_ARCHIVE_PREFIXES = (
    "corasdiagram/doc/latex/",
    "corasdiagram/tex/latex/",
)


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


def ignore_release_noise(_directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if (
            name.endswith(".bak")
            or name.endswith("~")
            or name == "__pycache__"
            or name == ".DS_Store"
        ):
            ignored.add(name)
    return ignored


def copy_tree(source: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest, ignore=ignore_release_noise)


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


def verify_bundle_layout(bundle_root: Path) -> None:
    missing = [
        relative_path
        for relative_path in REQUIRED_BUNDLE_PATHS
        if not (bundle_root / relative_path).exists()
    ]
    if missing:
        raise RuntimeError(
            f"release bundle missing expected paths: {', '.join(sorted(missing))}"
        )

    forbidden = [
        relative_path
        for relative_path in FORBIDDEN_BUNDLE_PREFIXES
        if (bundle_root / relative_path).exists()
    ]
    if forbidden:
        raise RuntimeError(
            "release bundle still contains forbidden nested paths: "
            + ", ".join(sorted(forbidden))
        )

    verify_runtime_icon_directory(bundle_root / "tex" / "icons")


def verify_archive_layout(archive_path: Path) -> None:
    with zipfile.ZipFile(archive_path) as archive:
        archive_names = set(archive.namelist())

    missing_files = [
        relative_path
        for relative_path in REQUIRED_ARCHIVE_FILES
        if relative_path not in archive_names
    ]
    if missing_files:
        raise RuntimeError(
            f"release archive missing expected files: {', '.join(sorted(missing_files))}"
        )

    missing_prefixes = [
        prefix
        for prefix in REQUIRED_ARCHIVE_PREFIXES
        if not any(name.startswith(prefix) for name in archive_names)
    ]
    if missing_prefixes:
        raise RuntimeError(
            "release archive missing expected file groups: "
            + ", ".join(sorted(missing_prefixes))
        )

    forbidden_prefixes = [
        prefix
        for prefix in FORBIDDEN_ARCHIVE_PREFIXES
        if any(name.startswith(prefix) for name in archive_names)
    ]
    if forbidden_prefixes:
        raise RuntimeError(
            "release archive still contains forbidden nested paths: "
            + ", ".join(sorted(forbidden_prefixes))
        )

    verify_runtime_icon_archive_names(archive_names)


def verify_runtime_icon_directory(icon_dir: Path) -> None:
    runtime_icons = sorted(icon_dir.glob("*.pdf"))
    if not runtime_icons:
        raise RuntimeError("release bundle is missing runtime icon PDFs in tex/icons.")

    invalid = [path.name for path in runtime_icons if not path.name.startswith(RUNTIME_ICON_PREFIX)]
    if invalid:
        raise RuntimeError(
            "release bundle contains unprefixed runtime icon PDFs: "
            + ", ".join(sorted(invalid))
        )


def verify_runtime_icon_archive_names(archive_names: set[str]) -> None:
    runtime_icons = sorted(
        name
        for name in archive_names
        if name.startswith("corasdiagram/tex/icons/") and name.endswith(".pdf")
    )
    if not runtime_icons:
        raise RuntimeError("release archive is missing runtime icon PDFs in corasdiagram/tex/icons/.")

    invalid = [
        name
        for name in runtime_icons
        if not Path(name).name.startswith(RUNTIME_ICON_PREFIX)
    ]
    if invalid:
        raise RuntimeError(
            "release archive contains unprefixed runtime icon PDFs: "
            + ", ".join(sorted(invalid))
        )


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    version = read_repo_version(repo_root)

    output_dir = args.output_dir.expanduser().resolve()
    bundle_root = output_dir / "ctan" / "corasdiagram"
    doc_root = bundle_root / "doc"
    tex_root = bundle_root / "tex"

    output_dir.mkdir(parents=True, exist_ok=True)
    if bundle_root.exists():
        shutil.rmtree(bundle_root)

    doc_root.mkdir(parents=True, exist_ok=True)
    tex_root.parent.mkdir(parents=True, exist_ok=True)

    copy_tree(repo_root / "tex" / "latex" / "corasdiagram", tex_root)
    copy_tree(repo_root / "assets" / "icons-src", bundle_root / "assets" / "icons-src")
    copy_example_sources(repo_root / "examples", doc_root / "examples")

    shutil.copy2(
        repo_root / "docs" / "corasdiagram-doc.tex",
        doc_root / "corasdiagram-doc.tex",
    )
    for filename in ("README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", "ROADMAP.md", "VERSION"):
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
    verify_bundle_layout(bundle_root)

    archive_path = output_dir / f"corasdiagram-{version}.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_root.rglob("*")):
            if path.is_file():
                relative_path = path.relative_to(bundle_root.parent)
                archive.write(path, relative_path.as_posix())
    verify_archive_layout(archive_path)

    print(f"wrote {bundle_root}")
    print(f"wrote {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
