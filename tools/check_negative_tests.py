#!/usr/bin/env python3
"""Compile the semantic failure fixtures and assert that they fail as expected."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the corasdiagram negative semantic regression tests."
    )
    parser.add_argument(
        "--engine",
        choices=("pdflatex", "lualatex"),
        default="pdflatex",
        help="TeX engine to use (default: pdflatex).",
    )
    parser.add_argument(
        "--expected-message",
        default="Package corasdiagram Error",
        help="Substring that must appear in failing compiler output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    tests_dir = repo_root / "tests" / "corasdiagram"
    test_files = sorted(tests_dir.glob("invalid-*.tex"))

    if not test_files:
        print(f"No test files found in {tests_dir}", file=sys.stderr)
        return 1

    texinputs = f"{repo_root / 'tex' / 'latex'}//:"
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="corasdiagram-negative-") as temp_dir:
        temp_root = Path(temp_dir)
        env = os.environ.copy()
        env["TEXINPUTS"] = texinputs
        env.setdefault("TEXMFVAR", str(temp_root / "texmf-var"))
        env.setdefault("TEXMFCACHE", env["TEXMFVAR"])

        for test_file in test_files:
            output_dir = temp_root / test_file.stem
            output_dir.mkdir(parents=True, exist_ok=True)
            command = [
                args.engine,
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={output_dir}",
                str(test_file),
            ]
            result = subprocess.run(
                command,
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
            )
            combined_output = result.stdout + result.stderr

            if result.returncode == 0:
                failures.append(f"{test_file.name}: expected failure, got success")
                continue

            if args.expected_message not in combined_output:
                failures.append(
                    f"{test_file.name}: missing expected message "
                    f"`{args.expected_message}`"
                )
                continue

            print(f"ok: {test_file.name}")

    if failures:
        print("negative semantic tests failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
