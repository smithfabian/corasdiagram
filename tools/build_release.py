#!/usr/bin/env python3
"""Assemble the CTAN-friendly release bundle for corasdiagram.

Inputs come from the canonical repository sources: VERSION, the package tree,
the built manual PDF, compiled example PDFs, and repo-root metadata files.
Contributors run this locally to smoke-test the release contents before
pushing a version tag.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path

from runtime_icons import RUNTIME_ICON_PREFIX
from versioning import read_repo_version

REQUIRED_BUNDLE_PATHS = (
    "NOTICE",
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
    "corasdiagram/NOTICE",
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


def tracked_example_stems(repo_root: Path) -> list[str]:
    examples_dir = repo_root / "examples"
    stems: set[str] = set()

    try:
        result = subprocess.run(
            ["git", "ls-files", "--", "examples"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        result = None
    else:
        for line in result.stdout.splitlines():
            path = Path(line.strip())
            if (
                path.parent == Path("examples")
                and path.suffix == ".tex"
                and (repo_root / path).is_file()
            ):
                stems.add(path.stem)
        if stems:
            return sorted(stems)

    if not examples_dir.is_dir():
        raise RuntimeError(
            f"Could not determine canonical examples: git is unavailable or "
            f"{repo_root} is not a git checkout, and there is no examples/ directory."
        )

    for tex_path in examples_dir.glob("*.tex"):
        if tex_path.is_file():
            stems.add(tex_path.stem)

    if not stems:
        raise RuntimeError(
            f"Could not determine canonical examples: no .tex files found in {examples_dir}."
        )

    return sorted(stems)


def copy_example_artifacts(
    repo_root: Path, source_dir: Path, dest_dir: Path, stems: list[str]
) -> None:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    for stem in stems:
        tex_path = source_dir / f"{stem}.tex"
        if not tex_path.exists():
            raise RuntimeError(f"Canonical example source is missing: {tex_path}")
        try:
            pdf_path = resolve_example_pdf(repo_root, stem)
        except RuntimeError as exc:
            raise RuntimeError(
                f"Missing compiled example PDF for {stem}. "
                f"Expected either examples/{stem}.pdf or {stem}.pdf at the repository root. "
                "Build the canonical examples (see CONTRIBUTING.md) before running "
                "tools/build_release.py."
            ) from exc
        shutil.copy2(tex_path, dest_dir / tex_path.name)
        shutil.copy2(pdf_path, dest_dir / pdf_path.name)

    fragments_dir = source_dir / "fragments"
    if fragments_dir.is_dir():
        copy_tree(fragments_dir, dest_dir / "fragments")


def resolve_example_pdf(repo_root: Path, stem: str) -> Path:
    """Resolve a canonical compiled example PDF from the repository tree only."""

    candidates = (
        repo_root / "examples" / f"{stem}.pdf",
        repo_root / f"{stem}.pdf",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise RuntimeError(f"Example PDF not found: {stem}.pdf")


def resolve_artifact(repo_root: Path, path: Path, *, label: str = "Artifact") -> Path:
    candidates = []
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.append((Path.cwd() / path).resolve())
        candidates.append((repo_root / path).resolve())
        candidates.append((repo_root / path.name).resolve())

    seen: set[Path] = set()
    non_files: list[Path] = []
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.is_file():
            return candidate
        if candidate.exists():
            non_files.append(candidate)

    if non_files:
        formatted = ", ".join(str(path) for path in non_files)
        raise RuntimeError(f"{label} is not a file: {formatted}")

    raise RuntimeError(f"{label} not found: {path}")


def verify_bundle_layout(bundle_root: Path, example_stems: list[str]) -> None:
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
    verify_example_directory(bundle_root / "doc" / "examples", example_stems)


def verify_archive_layout(archive_path: Path, example_stems: list[str]) -> None:
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
    verify_example_archive_names(archive_names, example_stems)


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


def verify_example_directory(example_dir: Path, example_stems: list[str]) -> None:
    missing = []
    for stem in example_stems:
        for suffix in (".tex", ".pdf"):
            path = example_dir / f"{stem}{suffix}"
            if not path.exists():
                missing.append(str(path))
    if missing:
        raise RuntimeError(
            "release bundle is missing canonical example artifacts: "
            + ", ".join(sorted(missing))
        )


def verify_example_archive_names(archive_names: set[str], example_stems: list[str]) -> None:
    missing = []
    for stem in example_stems:
        for suffix in (".tex", ".pdf"):
            name = f"corasdiagram/doc/examples/{stem}{suffix}"
            if name not in archive_names:
                missing.append(name)
    if missing:
        raise RuntimeError(
            "release archive is missing canonical example artifacts: "
            + ", ".join(sorted(missing))
        )


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    version = read_repo_version(repo_root)
    example_stems = tracked_example_stems(repo_root)

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
    copy_example_artifacts(
        repo_root, repo_root / "examples", doc_root / "examples", example_stems
    )

    shutil.copy2(
        repo_root / "manual" / "corasdiagram-doc.tex",
        doc_root / "corasdiagram-doc.tex",
    )
    for filename in (
        "README.md",
        "LICENSE",
        "NOTICE",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "VERSION",
    ):
        shutil.copy2(repo_root / filename, bundle_root / filename)

    doc_pdf = args.doc_pdf
    if doc_pdf is None:
        for candidate in (
            repo_root / "manual" / "corasdiagram-doc.pdf",
            repo_root / "corasdiagram-doc.pdf",
        ):
            if candidate.exists():
                doc_pdf = candidate
                break
    if doc_pdf is None:
        raise RuntimeError("Missing documentation PDF. Pass --doc-pdf after building docs.")

    doc_pdf = resolve_artifact(repo_root, doc_pdf.expanduser())

    shutil.copy2(doc_pdf, doc_root / "corasdiagram-doc.pdf")
    verify_bundle_layout(bundle_root, example_stems)

    archive_path = output_dir / f"corasdiagram-{version}.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(bundle_root.rglob("*")):
            if path.is_file():
                relative_path = path.relative_to(bundle_root.parent)
                archive.write(path, relative_path.as_posix())
    verify_archive_layout(archive_path, example_stems)

    print(f"wrote {bundle_root}")
    print(f"wrote {archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
