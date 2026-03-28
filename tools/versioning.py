#!/usr/bin/env python3
"""Shared version helpers for corasdiagram.

This module defines the canonical repository version story used by contributor
docs and the release workflow:

- VERSION is the repo-wide source of truth
- tex/latex/corasdiagram/corasdiagram-version.tex is the TeX runtime mirror
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
CHANGELOG_DATE_PATTERN = re.compile(
    r"^## \[(?P<version>[^\]]+)\] - (?P<date>\d{4}-\d{2}-\d{2})$",
    re.MULTILINE,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def version_file(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / "VERSION"


def tex_version_file(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / "tex" / "latex" / "corasdiagram" / "corasdiagram-version.tex"


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


def read_changelog_release_date(version: str, root: Path | None = None) -> str:
    text = changelog_file(root).read_text(encoding="utf-8")
    for match in CHANGELOG_DATE_PATTERN.finditer(text):
        if match.group("version").strip() == version:
            return match.group("date")
    raise RuntimeError(
        f"Could not find a dated CHANGELOG.md entry for release version {version!r}."
    )


def expected_tag(version: str) -> str:
    return f"v{version}"
