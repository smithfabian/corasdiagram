#!/usr/bin/env python3
"""Stage generated documentation assets into docs/assets/generated/.

The MkDocs site publishes built artifacts rather than compiling TeX itself.
This helper copies the already-built manual PDF and the canonical example
source/PDF pairs that currently exist in examples/ into the docs tree before
`mkdocs build`.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Stage manual and example assets for the MkDocs site."
    )
    parser.add_argument(
        "--doc-pdf",
        type=Path,
        required=True,
        help="Path to the built manual PDF.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "docs" / "assets" / "generated",
        help="Destination directory inside the docs tree.",
    )
    return parser.parse_args()


def example_stems(repo_root: Path) -> list[str]:
    stems = {
        path.stem
        for path in (repo_root / "examples").glob("*.tex")
        if path.is_file()
    }
    if not stems:
        raise RuntimeError("No canonical example sources found in examples/.")
    return sorted(stems)


def allowed_output_root(repo_root: Path) -> Path:
    return (repo_root / "docs" / "assets" / "generated").resolve()


def validate_output_dir(repo_root: Path, output_dir: Path) -> Path:
    output_root = output_dir.expanduser().resolve()
    generated_root = allowed_output_root(repo_root)

    if output_root == output_root.parent:
        raise RuntimeError(f"Refusing to stage into filesystem root: {output_root}")
    if output_root != generated_root and generated_root not in output_root.parents:
        raise RuntimeError(
            "Output dir must be the generated-docs tree or one of its descendants: "
            f"{generated_root}"
        )
    return output_root


def resolve_example_pdf(repo_root: Path, stem: str) -> Path:
    candidate = repo_root / "examples" / f"{stem}.pdf"
    if candidate.is_file():
        return candidate
    raise RuntimeError(
        f"Missing compiled example PDF for {stem} at {candidate}."
    )


def stage_assets(repo_root: Path, doc_pdf: Path, output_dir: Path) -> Path:
    output_root = validate_output_dir(repo_root, output_dir)
    manual_dir = output_root / "manual"
    examples_dir = output_root / "examples"

    if output_root.exists():
        shutil.rmtree(output_root)
    manual_dir.mkdir(parents=True, exist_ok=True)
    examples_dir.mkdir(parents=True, exist_ok=True)

    doc_pdf = doc_pdf.expanduser().resolve()
    if not doc_pdf.is_file():
        raise RuntimeError(f"Manual PDF not found: {doc_pdf}")
    shutil.copy2(doc_pdf, manual_dir / "corasdiagram-doc.pdf")

    for stem in example_stems(repo_root):
        tex_path = repo_root / "examples" / f"{stem}.tex"
        pdf_path = resolve_example_pdf(repo_root, stem)
        shutil.copy2(tex_path, examples_dir / tex_path.name)
        shutil.copy2(pdf_path, examples_dir / pdf_path.name)

    return output_root


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    output_root = stage_assets(repo_root, args.doc_pdf, args.output_dir)
    print(f"staged MkDocs assets in {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
