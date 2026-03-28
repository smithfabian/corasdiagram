#!/usr/bin/env python3
"""Ensure the release version story is internally consistent.

This script checks that VERSION and corasdiagram-version.tex agree, that the
LaTeX package header date in corasdiagram.sty matches the dated CHANGELOG.md
entry for the current version, and optionally that a pushed git tag matches
v<version>. It is used by the tagged release workflow and is also the quickest
local verification step before making or pushing a release tag.
"""

from __future__ import annotations

import argparse
import sys

from versioning import (
    expected_tag,
    iso_date_to_tex_date,
    read_changelog_release_date,
    read_package_header_date,
    read_repo_version,
    read_tex_version,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that VERSION, corasdiagram-version.tex, and a release tag agree."
    )
    parser.add_argument(
        "--tag",
        help="Optional git tag to validate against the canonical version.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    version = read_repo_version()
    tex_version = read_tex_version()
    changelog_date = read_changelog_release_date(version)
    package_header_date = read_package_header_date()
    expected_package_date = iso_date_to_tex_date(changelog_date)

    if version != tex_version:
        raise RuntimeError(
            f"VERSION ({version}) does not match corasdiagram-version.tex ({tex_version})."
        )
    if package_header_date != expected_package_date:
        raise RuntimeError(
            "corasdiagram.sty's \\ProvidesPackage date "
            f"({package_header_date}) does not match the current CHANGELOG.md "
            f"release date ({changelog_date}); expected TeX-formatted date "
            f"{expected_package_date!r}."
        )

    print(f"VERSION: {version}")
    print(f"TeX runtime version: {tex_version}")
    print(f"CHANGELOG release date: {changelog_date}")
    print(f"Package header date: {package_header_date}")

    if args.tag:
        expected = expected_tag(version)
        if args.tag != expected:
            raise RuntimeError(
                f"Release tag {args.tag!r} does not match VERSION; expected {expected!r}."
            )
        print(f"Release tag matches VERSION: {args.tag}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
