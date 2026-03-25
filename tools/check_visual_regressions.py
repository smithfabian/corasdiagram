#!/usr/bin/env python3
"""Compile visual fixtures and compare them to committed snapshot baselines."""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Fixture:
    source: Path
    pages: tuple[int, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run visual regression checks for corasdiagram."
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update committed snapshot baselines from the current render output.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        help="Optional directory to populate with actual rendered PNGs and compile logs.",
    )
    return parser.parse_args()


def fixture_inventory(repo_root: Path) -> dict[str, Fixture]:
    return {
        "corasdiagram-minimal": Fixture(
            source=repo_root / "examples" / "corasdiagram-minimal.tex",
            pages=(1,),
        ),
        "corasdiagram-demo": Fixture(
            source=repo_root / "examples" / "corasdiagram-demo.tex",
            pages=(1, 2, 3),
        ),
        # The high-level analysis table is still compile-tested in CI, but not
        # snapshot-tested here because longtable text wrapping drifts across TeX
        # toolchains and causes false-positive byte-level PNG diffs.
        "auto-layout-regression": Fixture(
            source=repo_root / "tests" / "corasdiagram" / "auto-layout-regression.tex",
            pages=(1, 2, 3, 4, 5),
        ),
        "endpoint-geometry-regression": Fixture(
            source=repo_root / "tests" / "corasdiagram" / "endpoint-geometry-regression.tex",
            pages=(1,),
        ),
        "icon-auto-edge-regression": Fixture(
            source=repo_root / "tests" / "corasdiagram" / "icon-auto-edge-regression.tex",
            pages=(1, 2),
        ),
        "icon-anchor-regression": Fixture(
            source=repo_root / "tests" / "corasdiagram" / "icon-anchor-regression.tex",
            pages=(1, 2, 3, 4),
        ),
        "min-edge-gap-regression": Fixture(
            source=repo_root / "tests" / "corasdiagram" / "min-edge-gap-regression.tex",
            pages=(1,),
        ),
    }


def ensure_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required tool `{name}` not found on PATH")


def run_command(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )


def write_artifact_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def compile_fixture(
    stem: str,
    fixture: Fixture,
    repo_root: Path,
    temp_root: Path,
    env: dict[str, str],
    artifact_dir: Path | None,
) -> Path:
    output_dir = temp_root / "latex" / stem
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={output_dir}",
        str(fixture.source),
    ]
    result = run_command(command, cwd=repo_root, env=env)

    if artifact_dir is not None:
        write_artifact_text(
            artifact_dir / f"{stem}-compile.txt",
            "$ " + " ".join(command) + "\n\n" + result.stdout + result.stderr,
        )

    pdf_path = output_dir / f"{fixture.source.stem}.pdf"
    log_path = output_dir / f"{fixture.source.stem}.log"
    if artifact_dir is not None and log_path.exists():
        shutil.copy2(log_path, artifact_dir / f"{stem}.log")

    if result.returncode != 0:
        raise RuntimeError(
            f"{fixture.source.name}: pdflatex failed\n{result.stdout}{result.stderr}"
        )
    if not pdf_path.exists():
        raise RuntimeError(f"{fixture.source.name}: expected PDF `{pdf_path}` was not created")
    return pdf_path


def rasterize_fixture(stem: str, pdf_path: Path, temp_root: Path) -> dict[int, Path]:
    render_dir = temp_root / "renders" / stem
    render_dir.mkdir(parents=True, exist_ok=True)
    prefix = render_dir / stem
    command = ["pdftoppm", "-r", "216", "-png", str(pdf_path), str(prefix)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{pdf_path.name}: pdftoppm failed\n{result.stdout}{result.stderr}")

    rendered: dict[int, Path] = {}
    for path in sorted(render_dir.glob(f"{stem}-*.png")):
        page = int(path.stem.rsplit("-", 1)[1])
        rendered[page] = path
    if not rendered:
        raise RuntimeError(f"{pdf_path.name}: no PNG snapshots were produced")
    return rendered


def copy_actual_renders(rendered: dict[int, Path], stem: str, artifact_dir: Path | None) -> None:
    if artifact_dir is None:
        return
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for page, path in rendered.items():
        shutil.copy2(path, artifact_dir / f"{stem}-p{page}.png")


def snapshot_name(stem: str, page: int) -> str:
    return f"{stem}-p{page}.png"


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    snapshots_dir = repo_root / "tests" / "corasdiagram" / "snapshots"
    fixtures = fixture_inventory(repo_root)

    ensure_tool("pdflatex")
    ensure_tool("pdftoppm")

    artifact_dir: Path | None = None
    if args.artifact_dir is not None:
        artifact_dir = args.artifact_dir.expanduser().resolve()
        if artifact_dir.exists():
            shutil.rmtree(artifact_dir)
        artifact_dir.mkdir(parents=True, exist_ok=True)

    texinputs = f"{repo_root / 'tex' / 'latex'}//:"
    failures: list[str] = []
    expected_snapshot_files: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="corasdiagram-visual-") as temp_dir:
        temp_root = Path(temp_dir)
        env = os.environ.copy()
        env["TEXINPUTS"] = texinputs
        env.setdefault("TEXMFVAR", str(temp_root / "texmf-var"))
        env.setdefault("TEXMFCACHE", env["TEXMFVAR"])

        for stem, fixture in fixtures.items():
            try:
                pdf_path = compile_fixture(
                    stem=stem,
                    fixture=fixture,
                    repo_root=repo_root,
                    temp_root=temp_root,
                    env=env,
                    artifact_dir=artifact_dir,
                )
                rendered = rasterize_fixture(stem=stem, pdf_path=pdf_path, temp_root=temp_root)
            except RuntimeError as exc:
                failures.append(str(exc))
                continue

            copy_actual_renders(rendered=rendered, stem=stem, artifact_dir=artifact_dir)

            actual_pages = set(rendered)
            expected_pages = set(fixture.pages)
            if actual_pages != expected_pages:
                failures.append(
                    f"{fixture.source.name}: expected pages {sorted(expected_pages)}, "
                    f"got {sorted(actual_pages)}"
                )

            for page in fixture.pages:
                name = snapshot_name(stem, page)
                expected_snapshot_files.add(name)
                actual = rendered.get(page)
                if actual is None:
                    continue
                if args.update:
                    snapshots_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(actual, snapshots_dir / name)
                    continue

                baseline = snapshots_dir / name
                if not baseline.exists():
                    failures.append(f"missing baseline snapshot: {baseline.relative_to(repo_root)}")
                    continue
                if not filecmp.cmp(baseline, actual, shallow=False):
                    failures.append(f"snapshot changed: {baseline.relative_to(repo_root)}")

        if args.update:
            for path in snapshots_dir.glob("*.png"):
                if path.name not in expected_snapshot_files:
                    path.unlink()
            print(f"updated {len(expected_snapshot_files)} snapshot(s) in {snapshots_dir}")
            return 0

    existing_snapshot_files = set()
    if snapshots_dir.exists():
        existing_snapshot_files = {path.name for path in snapshots_dir.glob("*.png")}

    extra_snapshots = sorted(existing_snapshot_files - expected_snapshot_files)
    if extra_snapshots:
        failures.append(
            "unexpected baseline snapshots: "
            + ", ".join(str((snapshots_dir / name).relative_to(repo_root)) for name in extra_snapshots)
        )

    if failures:
        print("visual regression tests failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        if artifact_dir is not None:
            print(f"actual renders copied to {artifact_dir}", file=sys.stderr)
        return 1

    print("visual regression tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
