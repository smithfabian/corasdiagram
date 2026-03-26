#!/usr/bin/env python3
"""Ensure the release version story is internally consistent.

This script checks that VERSION and corasdiagram-version.tex agree, and
optionally that a pushed git tag matches v<version>. It is used by the tagged
release workflow and is also the quickest local verification step before making
or pushing a release tag.
"""

from __future__ import annotations

import argparse
import sys

from versioning import expected_tag, read_repo_version, read_tex_version


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

    if version != tex_version:
        raise RuntimeError(
            f"VERSION ({version}) does not match corasdiagram-version.tex ({tex_version})."
        )

    print(f"VERSION: {version}")
    print(f"TeX runtime version: {tex_version}")

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
