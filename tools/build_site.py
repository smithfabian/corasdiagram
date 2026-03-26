#!/usr/bin/env python3
"""Build the static documentation site published by the Pages workflow.

The site is generated from prebuilt manual/example PDFs plus VERSION. This is a
packaging helper, not a source of truth: the package, docs, and examples stay
in the repository, while dist/site/ is disposable output.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from versioning import read_repo_version


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Build a static documentation site for corasdiagram."
    )
    parser.add_argument("--docs-pdf", type=Path, required=True, help="Manual PDF.")
    parser.add_argument("--demo-pdf", type=Path, required=True, help="Demo PDF.")
    parser.add_argument(
        "--minimal-pdf", type=Path, required=True, help="Minimal example PDF."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "dist" / "site",
        help="Output directory for the generated site.",
    )
    return parser.parse_args()


def resolve_artifact(repo_root: Path, path: Path) -> Path:
    candidates = []
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.append((Path.cwd() / path).resolve())
        candidates.append((repo_root / path).resolve())
        candidates.append((repo_root / path.name).resolve())

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists():
            return candidate

    raise FileNotFoundError(path)


def rasterize(pdf_path: Path, prefix: Path, first: int | None = None, last: int | None = None) -> None:
    command = ["pdftoppm", "-png"]
    if first is not None:
        command.extend(["-f", str(first)])
    if last is not None:
        command.extend(["-l", str(last)])
    command.extend([str(pdf_path), str(prefix)])
    subprocess.run(command, check=True)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    args = parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    version = read_repo_version(repo_root)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    docs_pdf = resolve_artifact(repo_root, args.docs_pdf.expanduser())
    demo_pdf = resolve_artifact(repo_root, args.demo_pdf.expanduser())
    minimal_pdf = resolve_artifact(repo_root, args.minimal_pdf.expanduser())

    shutil.copy2(docs_pdf, output_dir / "corasdiagram-doc.pdf")

    rasterize(demo_pdf, output_dir / "demo", first=1, last=3)
    rasterize(minimal_pdf, output_dir / "minimal", first=1, last=1)

    index_html = output_dir / "index.html"
    index_html.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>corasdiagram {version}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      padding: 2rem;
      color: #1f2933;
      background: #f5f7fa;
    }}
    main {{
      max-width: 72rem;
      margin: 0 auto;
    }}
    h1, h2 {{
      margin-top: 0;
    }}
    .card {{
      background: white;
      border: 1px solid #d9e2ec;
      border-radius: 12px;
      padding: 1.25rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }}
    img {{
      max-width: 100%;
      display: block;
      border: 1px solid #d9e2ec;
      border-radius: 10px;
      margin-bottom: 1rem;
      background: white;
    }}
    .grid {{
      display: grid;
      gap: 1rem;
    }}
    @media (min-width: 960px) {{
      .grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="card">
      <h1>corasdiagram {version}</h1>
      <p>
        Open-source CORAS diagram package release artifacts.
      </p>
      <p>
        <a href="corasdiagram-doc.pdf">Download the manual PDF</a>
      </p>
    </section>
    <section class="card">
      <h2>Minimal Example</h2>
      <img src="minimal-1.png" alt="Minimal asset diagram example">
    </section>
    <section class="card">
      <h2>Full Demo</h2>
      <div class="grid">
        <img src="demo-1.png" alt="Demo page 1">
        <img src="demo-2.png" alt="Demo page 2">
        <img src="demo-3.png" alt="Demo page 3">
      </div>
    </section>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )

    print(f"wrote {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
