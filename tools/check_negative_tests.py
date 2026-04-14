#!/usr/bin/env python3
"""Run the curated negative semantic regression fixtures.

The semantic-first refactor intentionally removed part of the historical public
surface. The authoritative negative suite therefore covers three buckets:

- removed commands, keys, and scope options that must fail with replacement
  guidance
- invalid semantic relations on the canonical surface
- compatibility edge cases such as `\\cause` ambiguity
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NegativeFixture:
    source: str
    expected_message: str


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
    return parser.parse_args()


def fixture_inventory() -> tuple[NegativeFixture, ...]:
    generic = "Package corasdiagram Error"
    return (
        NegativeFixture("removed-command-negative.tex", r"\stakeholder has been removed"),
        NegativeFixture("removed-wrapper-negative.tex", r"\corasasset has been removed"),
        NegativeFixture("removed-scope-key-negative.tex", "Scope key `stakeholder` has been removed"),
        NegativeFixture("removed-node-key-negative.tex", "Node key `level` has been removed"),
        NegativeFixture("removed-node-key-meta-negative.tex", "Node key `meta` has been removed"),
        NegativeFixture("removed-node-key-value-negative.tex", "Node key `value` has been removed"),
        NegativeFixture(
            "removed-node-key-likelihood-label-negative.tex",
            "Node key `likelihood label` has been removed",
        ),
        NegativeFixture("removed-edge-key-negative.tex", "Edge key `via` has been removed"),
        NegativeFixture(
            "removed-edge-key-probability-negative.tex",
            "Edge key `probability` has been removed",
        ),
        NegativeFixture("invalid-impacts-negative.tex", generic),
        NegativeFixture("invalid-initiates-negative.tex", generic),
        NegativeFixture("invalid-leadsto-negative.tex", generic),
        NegativeFixture("invalid-treats-negative.tex", generic),
        NegativeFixture("invalid-cause-ambiguous-negative.tex", r"\cause is ambiguous"),
        NegativeFixture("invalid-low-level-node-in-asset.tex", generic),
        NegativeFixture("invalid-typed-duplicate-id.tex", generic),
        NegativeFixture("invalid-typed-unknown-id.tex", generic),
        NegativeFixture("invalid-typed-wrong-family-edge.tex", generic),
    )


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    tests_dir = repo_root / "tests" / "corasdiagram"
    fixtures = fixture_inventory()

    if not fixtures:
        print("No negative fixtures configured", file=sys.stderr)
        return 1

    texinputs = f"{repo_root / 'tex' / 'latex'}//:"
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="corasdiagram-negative-") as temp_dir:
        temp_root = Path(temp_dir)
        env = os.environ.copy()
        env["TEXINPUTS"] = texinputs
        env.setdefault("TEXMFVAR", str(temp_root / "texmf-var"))
        env.setdefault("TEXMFCACHE", env["TEXMFVAR"])

        for fixture in fixtures:
            test_file = tests_dir / fixture.source
            if not test_file.exists():
                failures.append(f"{fixture.source}: fixture file is missing")
                continue

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

            if fixture.expected_message not in combined_output:
                failures.append(
                    f"{test_file.name}: missing expected message "
                    f"`{fixture.expected_message}`"
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
