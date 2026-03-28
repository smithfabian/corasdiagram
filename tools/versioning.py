#!/usr/bin/env python3
"""Shared version helpers for corasdiagram.

This module defines the canonical repository version story used by contributor
docs and the release workflow:

- VERSION is the repo-wide source of truth
- tex/latex/corasdiagram/corasdiagram-version.tex is the TeX runtime mirror
- tex/latex/corasdiagram/corasdiagram.sty carries the LaTeX package header date
- CHANGELOG.md carries the dated release entries used for CTAN uploads
- release tags must be v<version>

Contributors typically use this module indirectly through check_release_tag.py,
build_release.py, build_site.py, and upload_ctan.py.
"""

from __future__ import annotations

import re
from pathlib import Path


VERSION_PATTERN = re.compile(r"^[0-9]+(?:\.[0-9]+)*(?:[-+][A-Za-z0-9.-]+)?$")
TEX_VERSION_PATTERN = re.compile(
    r"\\def\\corasdiagramversion\{([^}]+)\}"
)
PACKAGE_DATE_PATTERN = re.compile(
    r"\\ProvidesPackage\{corasdiagram\}\[(\d{4}/\d{2}/\d{2})\s+v"
)
CHANGELOG_DATE_PATTERN = re.compile(
    r"^## \[(?P<version>[^\]]+)\] - (?P<date>\d{4}-\d{2}-\d{2})$"
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def version_file(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / "VERSION"


def tex_version_file(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / "tex" / "latex" / "corasdiagram" / "corasdiagram-version.tex"


def sty_file(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / "tex" / "latex" / "corasdiagram" / "corasdiagram.sty"


def changelog_file(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / "CHANGELOG.md"


def read_repo_version(root: Path | None = None) -> str:
    text = version_file(root).read_text(encoding="utf-8").strip()
    if not VERSION_PATTERN.fullmatch(text):
        raise RuntimeError(f"Invalid VERSION value: {text!r}")
    return text


def read_tex_version(root: Path | None = None) -> str:
    text = tex_version_file(root).read_text(encoding="utf-8")
    match = TEX_VERSION_PATTERN.search(text)
    if not match:
        raise RuntimeError("Could not find \\corasdiagramversion in corasdiagram-version.tex")
    return match.group(1).strip()


def read_package_header_date(root: Path | None = None) -> str:
    text = sty_file(root).read_text(encoding="utf-8")
    match = PACKAGE_DATE_PATTERN.search(text)
    if not match:
        raise RuntimeError(
            "Could not find the corasdiagram \\ProvidesPackage date in corasdiagram.sty"
        )
    return match.group(1).strip()


def read_changelog_release_date(version: str, root: Path | None = None) -> str:
    text = changelog_file(root).read_text(encoding="utf-8")
    for line in text.splitlines():
        match = CHANGELOG_DATE_PATTERN.match(line.strip())
        if match is None:
            continue
        if match.group("version").strip() == version:
            return match.group("date")
    raise RuntimeError(
        f"Could not find a dated CHANGELOG.md entry for release version {version!r}."
    )


def iso_date_to_tex_date(date_text: str) -> str:
    parts = date_text.split("-")
    if len(parts) != 3 or any(not part for part in parts):
        raise RuntimeError(f"Invalid ISO release date: {date_text!r}")
    year, month, day = parts
    return f"{year}/{month}/{day}"


def expected_tag(version: str) -> str:
    return f"v{version}"
