#!/usr/bin/env python3
"""Run the compact semantic-first release gate for corasdiagram.

The semantic-first refactor has a narrower release boundary than the historical
package surface. This script makes that boundary explicit by checking:

- canonical semantic fixtures
- retained compatibility fixtures
- repo-facing docs and public examples
- curated negative semantic/removal fixtures
- authoritative visual regression baselines
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
class CompileFixture:
    group: str
    source: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the semantic-first corasdiagram release gate."
    )
    parser.add_argument(
        "--engine",
        choices=("pdflatex", "lualatex"),
        default="pdflatex",
        help="TeX engine for positive compile checks (default: pdflatex).",
    )
    parser.add_argument(
        "--skip-visual",
        action="store_true",
        help="Skip visual regression checks.",
    )
    return parser.parse_args()


def fixture_inventory(repo_root: Path) -> tuple[CompileFixture, ...]:
    example_fixtures = tuple(
        CompileFixture("docs", path)
        for path in sorted((repo_root / "examples").glob("*.tex"))
        if path.is_file()
    )
    return (
        CompileFixture("canonical", repo_root / "tests" / "corasdiagram" / "semantic-asset-regression.tex"),
        CompileFixture("canonical", repo_root / "tests" / "corasdiagram" / "semantic-threat-regression.tex"),
        CompileFixture("canonical", repo_root / "tests" / "corasdiagram" / "semantic-risk-regression.tex"),
        CompileFixture("canonical", repo_root / "tests" / "corasdiagram" / "semantic-treatment-regression.tex"),
        CompileFixture(
            "canonical",
            repo_root / "tests" / "corasdiagram" / "semantic-treatment-overview-regression.tex",
        ),
        CompileFixture(
            "compatibility",
            repo_root / "tests" / "corasdiagram" / "compatibility-alias-regression.tex",
        ),
        CompileFixture("docs", repo_root / "tests" / "corasdiagram" / "readme-regression.tex"),
        CompileFixture(
            "docs",
            repo_root / "tests" / "corasdiagram" / "migration-guide-regression.tex",
        ),
        *example_fixtures,
        CompileFixture("docs", repo_root / "manual" / "corasdiagram-doc.tex"),
    )


def run_command(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )


def compile_fixture(
    fixture: CompileFixture,
    output_dir: Path,
    repo_root: Path,
    env: dict[str, str],
    engine: str,
) -> None:
    latexmk_engine = "-pdf" if engine == "pdflatex" else "-lualatex"
    command = [
        "latexmk",
        latexmk_engine,
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-outdir={output_dir}",
        str(fixture.source),
    ]
    result = run_command(command, cwd=repo_root, env=env)
    if result.returncode != 0:
        raise RuntimeError(
            f"{fixture.group}:{fixture.source.name}: latexmk failed\n"
            f"{result.stdout}{result.stderr}"
        )


def run_helper(helper: list[str], repo_root: Path, env: dict[str, str]) -> None:
    result = run_command(helper, cwd=repo_root, env=env)
    if result.returncode != 0:
        raise RuntimeError("$ " + " ".join(helper) + "\n\n" + result.stdout + result.stderr)


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    fixtures = fixture_inventory(repo_root)
    failures: list[str] = []

    texinputs = f"{repo_root / 'tex' / 'latex'}//:"
    with tempfile.TemporaryDirectory(prefix="corasdiagram-release-gate-") as temp_dir:
        temp_root = Path(temp_dir)
        env = os.environ.copy()
        env["TEXINPUTS"] = texinputs
        env.setdefault("TEXMFVAR", str(temp_root / "texmf-var"))
        env.setdefault("TEXMFCACHE", env["TEXMFVAR"])

        for fixture in fixtures:
            output_dir = temp_root / fixture.group / fixture.source.stem
            output_dir.mkdir(parents=True, exist_ok=True)
            try:
                compile_fixture(
                    fixture=fixture,
                    output_dir=output_dir,
                    repo_root=repo_root,
                    env=env,
                    engine=args.engine,
                )
                print(f"ok: {fixture.group}: {fixture.source.name}")
            except RuntimeError as exc:
                failures.append(str(exc))

        try:
            run_helper(
                ["python3", "tools/check_negative_tests.py", "--engine", args.engine],
                repo_root=repo_root,
                env=env,
            )
        except RuntimeError as exc:
            failures.append(str(exc))

        if not args.skip_visual:
            try:
                run_helper(
                    ["python3", "tools/check_visual_regressions.py"],
                    repo_root=repo_root,
                    env=env,
                )
            except RuntimeError as exc:
                failures.append(str(exc))

    if failures:
        print("release gate failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("release gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
