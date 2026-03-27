#!/usr/bin/env python3
"""Build the static documentation site published by the Pages workflow.

The site is generated from checked-in site templates plus prebuilt package
artifacts. This keeps the homepage maintainable without introducing a frontend
framework:

- VERSION is the release number shown on the page
- ctan/metadata.json provides the package summary/description
- manual/example PDFs are rasterized into preview images
- site-src/ contains the homepage template and static assets

The generated dist/site/ tree is disposable output.
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
from pathlib import Path
from textwrap import dedent

from versioning import read_repo_version


REPO_URL = "https://github.com/smithfabian/corasdiagram"
ISSUES_URL = f"{REPO_URL}/issues"
RELEASES_URL = f"{REPO_URL}/releases"

MINIMAL_SNIPPET = dedent(
    r"""
    \documentclass{article}
    \usepackage{corasdiagram}

    \begin{document}
    \begin{corasassetdiagram}[x=1cm,y=1cm]
      \corasstakeholder[name=stakeholder,scope=asset-scope,title={Stakeholder}]
      \corasasset[name=asset,scope=asset-scope,title={Asset}]
      \corasindirectasset[name=indirect,scope=asset-scope,title={Indirect\\Asset}]
      \corasscope[
        name=asset-box,
        scope=asset-scope,
        kind=asset-scope,
        stakeholder=stakeholder,
        stakeholder corner=left
      ]
      \corasrelates[from=asset,to=indirect]
    \end{corasassetdiagram}
    \end{document}
    """
).strip()

HOW_IT_WORKS_SNIPPET = dedent(
    r"""
    \begin{corasthreatdiagram}[x=1cm,y=1cm]
      \corasthreataccidental[name=employee,title={Employee}]
      \corasvulnerability[name=web,title={Old version of\\webserver}]
      \corasscenario[name=scenario,title={Servers infected},meta={1 per year}]
      \corasunwantedincident[name=incident,title={Disclosure of data}]
      \corasasset[name=asset,title={Data privacy}]

      \corascauses[from=employee,to=web]
      \corascauses[from=web,to=scenario]
      \corascauses[from=scenario,to=incident]
      \corasrelates[from=incident,to=asset]
    \end{corasthreatdiagram}
    """
).strip()


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
        "--website-examples-pdf",
        type=Path,
        required=True,
        help="Website-oriented examples PDF (diagram + table pages).",
    )
    parser.add_argument(
        "--analysis-table-pdf",
        type=Path,
        required=True,
        help="High-level analysis table PDF.",
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


def rasterize(
    pdf_path: Path, prefix: Path, *, first: int | None = None, last: int | None = None
) -> None:
    command = ["pdftoppm", "-png"]
    if first is not None:
        command.extend(["-f", str(first)])
    if last is not None:
        command.extend(["-l", str(last)])
    command.extend([str(pdf_path), str(prefix)])
    subprocess.run(command, check=True)


def render_code_block(block_id: str, title: str, code: str) -> str:
    escaped = html.escape(code)
    return dedent(
        f"""
        <article class="code-card">
          <div class="code-card__header">
            <h3>{html.escape(title)}</h3>
            <button class="copy-button" type="button" data-copy-target="{block_id}">Copy</button>
          </div>
          <pre><code id="{block_id}">{escaped}</code></pre>
        </article>
        """
    ).strip()


def render_capability_cards() -> str:
    cards = [
        ("Asset diagrams", "Stakeholders, direct assets, indirect assets, and scoped asset structures."),
        ("Threat diagrams", "Threat sources, vulnerabilities, scenarios, unwanted incidents, and harmed assets."),
        ("Risk diagrams", "Risk-focused views that connect threat sources, risks, and impacted assets."),
        ("Treatment diagrams", "Treatment chains that show how mitigations relate to selected threats and incidents."),
        ("Treatment overview diagrams", "Overview views with risks, treatments, assets, and fan-in through a junction."),
        ("High-level analysis tables", "CORAS-style report tables with the package-managed header icon groups."),
    ]
    return "\n".join(
        dedent(
            f"""
            <article class="capability-card">
              <h3>{html.escape(title)}</h3>
              <p>{html.escape(description)}</p>
            </article>
            """
        ).strip()
        for title, description in cards
    )


def render_example_cards() -> str:
    cards = [
        ("Minimal asset example", "minimal-1.png", "Minimal asset diagram with stakeholder, direct asset, and indirect asset."),
        ("Demo page 1", "demo-1.png", "Asset and threat diagram examples from the full demo document."),
        ("Demo page 2", "demo-2.png", "Risk and treatment diagram examples from the full demo document."),
        ("Demo page 3", "demo-3.png", "Treatment overview example and additional reference content from the full demo."),
        ("High-level analysis table", "analysis-table-1.png", "CORAS high-level analysis table preview rendered from the package example."),
    ]
    return "\n".join(
        dedent(
            f"""
            <article class="gallery-card">
              <img src="{src}" alt="{html.escape(alt)}">
              <div class="gallery-card__body">
                <h3>{html.escape(title)}</h3>
                <p>{html.escape(alt)}</p>
              </div>
            </article>
            """
        ).strip()
        for title, src, alt in cards
    )


def render_diagram_examples() -> str:
    examples = [
        ("Asset Diagram", "website-example-1.png", "website-snippet-asset", dedent(r"""
\begin{corasassetdiagram}
  \corasstakeholder[name=stakeholder,scope=asset-scope,title={Stakeholder}]
  \corasasset[name=asset,scope=asset-scope,title={Customer Data}]
  \corasindirectasset[name=brand,scope=asset-scope,title={Brand Reputation}]
  \corasscope[name=scope,scope=asset-scope,kind=asset-scope,stakeholder=stakeholder,stakeholder corner=left]
  \corasrelates[from=asset,to=brand]
\end{corasassetdiagram}
""").strip()),
        ("Threat Diagram", "website-example-2.png", "website-snippet-threat", dedent(r"""
\begin{corasthreatdiagram}
  \corasthreataccidental[name=human,title={Employee mistake}]
  \corasvulnerability[name=vuln,title={Weak access policy}]
  \corasscenario[name=sc,title={Misconfigured endpoint},meta={2/year}]
  \corasunwantedincident[name=inc,title={Data exposure}]
  \corasasset[name=asset,title={Customer data}]
  \corascauses[from=human,to=vuln]
  \corascauses[from=vuln,to=sc]
  \corascauses[from=sc,to=inc]
  \corasrelates[from=inc,to=asset]
\end{corasthreatdiagram}
""").strip()),
        ("Risk Diagram", "website-example-3.png", "website-snippet-risk", dedent(r"""
\begin{corasriskdiagram}
  \corasthreatdeliberate[name=attacker,title={External attacker}]
  \corasrisk[name=risk,title={Data breach},level={High}]
  \corasasset[name=asset,title={Customer data}]
  \corascauses[from=attacker,to=risk]
  \corasrelates[from=risk,to=asset]
\end{corasriskdiagram}
""").strip()),
        ("Treatment Diagram", "website-example-4.png", "website-snippet-treatment", dedent(r"""
\begin{corastreatmentdiagram}
  \corasthreatdeliberate[name=attacker,title={Attacker}]
  \corasvulnerability[name=vuln,title={Weak MFA policy}]
  \corasscenario[name=sc,title={Compromised account},meta={1/year}]
  \corasunwantedincident[name=inc,title={Unauthorized access}]
  \corasasset[name=asset,title={Payment service}]
  \corastreatment[name=ctrl,title={Enforce phishing-resistant MFA}]
  \corastreats[from=ctrl,to=sc]
\end{corastreatmentdiagram}
""").strip()),
        ("Treatment Overview Diagram", "website-example-5.png", "website-snippet-overview", dedent(r"""
\begin{corastreatmentoverviewdiagram}
  \corasrisk[name=r1,title={Credential theft},level={High}]
  \corasrisk[name=r2,title={Session hijack},level={Medium}]
  \corasasset[name=a1,title={User accounts}]
  \corastreatment[name=t1,title={Hardware keys}]
  \corasjunction[name=j1]
  \corastreats[from=t1,to=j1]
  \corastreats[from=j1,to=r1]
  \corastreats[from=j1,to=r2]
\end{corastreatmentoverviewdiagram}
""").strip()),
        ("High-Level Analysis Table", "website-example-6.png", "website-snippet-table", dedent(r"""
\begin{corashighlevelanalysistable}[caption={High-level analysis excerpt}]
  \corashighlevelanalysisrow
    {Hacker}
    {Compromises confidentiality of customer records}
    {Weak access controls on remote interfaces}
\end{corashighlevelanalysistable}
""").strip()),
    ]
    blocks: list[str] = []
    for title, image_name, block_id, snippet in examples:
        blocks.append(
            dedent(
                f"""
                <article class="example-row">
                  <div class="example-row__visual preview-frame">
                    <img src="{image_name}" alt="{html.escape(title)} example preview">
                  </div>
                  {render_code_block(block_id, title, snippet)}
                </article>
                """
            ).strip()
        )
    return "\n".join(blocks)


def render_next_steps() -> str:
    links = [
        ("Download the manual PDF", "corasdiagram-doc.pdf"),
        ("Browse the repository", REPO_URL),
        ("View releases", RELEASES_URL),
        ("Report an issue", ISSUES_URL),
    ]
    return "\n".join(
        f'<li><a href="{href}">{html.escape(label)}</a></li>'
        for label, href in links
    )


def load_metadata(repo_root: Path) -> dict[str, object]:
    metadata_path = repo_root / "ctan" / "metadata.json"
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def copy_static_assets(source_dir: Path, output_dir: Path) -> None:
    for path in source_dir.iterdir():
        if path.name == "index.html":
            continue
        destination = output_dir / path.name
        if path.is_dir():
            shutil.copytree(path, destination)
        else:
            shutil.copy2(path, destination)


def render_index(template_text: str, replacements: dict[str, str]) -> str:
    rendered = template_text
    for key, value in replacements.items():
        rendered = rendered.replace(f"__{key}__", value)
    return rendered


def verify_site_output(output_dir: Path) -> None:
    required_files = [
        "index.html",
        "styles.css",
        "app.js",
        "corasdiagram-doc.pdf",
        "minimal-1.png",
        "demo-1.png",
        "demo-2.png",
        "demo-3.png",
        "analysis-table-1.png",
        "website-example-1.png",
        "website-example-2.png",
        "website-example-3.png",
        "website-example-4.png",
        "website-example-5.png",
        "website-example-6.png",
    ]
    missing = [name for name in required_files if not (output_dir / name).exists()]
    if missing:
        raise RuntimeError(f"site build missing expected files: {', '.join(missing)}")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    args = parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    site_source_dir = repo_root / "site-src"
    version = read_repo_version(repo_root)
    metadata = load_metadata(repo_root)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    docs_pdf = resolve_artifact(repo_root, args.docs_pdf.expanduser())
    demo_pdf = resolve_artifact(repo_root, args.demo_pdf.expanduser())
    minimal_pdf = resolve_artifact(repo_root, args.minimal_pdf.expanduser())
    analysis_table_pdf = resolve_artifact(repo_root, args.analysis_table_pdf.expanduser())
    website_examples_pdf = resolve_artifact(
        repo_root, args.website_examples_pdf.expanduser()
    )

    shutil.copy2(docs_pdf, output_dir / "corasdiagram-doc.pdf")
    copy_static_assets(site_source_dir, output_dir)

    rasterize(demo_pdf, output_dir / "demo", first=1, last=3)
    rasterize(minimal_pdf, output_dir / "minimal", first=1, last=1)
    rasterize(analysis_table_pdf, output_dir / "analysis-table", first=1, last=1)
    rasterize(website_examples_pdf, output_dir / "website-example", first=1, last=6)

    template_text = (site_source_dir / "index.html").read_text(encoding="utf-8")
    index_html = output_dir / "index.html"
    index_html.write_text(
        render_index(
            template_text,
            {
                "PAGE_TITLE": f"corasdiagram {html.escape(version)}",
                "VERSION": html.escape(version),
                "SUMMARY": html.escape(str(metadata["summary"])),
                "DESCRIPTION": html.escape(str(metadata["description"])),
                "REPO_URL": REPO_URL,
                "ISSUES_URL": ISSUES_URL,
                "RELEASES_URL": RELEASES_URL,
                "CAPABILITY_CARDS": render_capability_cards(),
                "MINIMAL_SNIPPET": render_code_block(
                    "minimal-snippet",
                    "Minimal semantic example",
                    MINIMAL_SNIPPET,
                ),
                "HOW_IT_WORKS_SNIPPET": render_code_block(
                    "how-it-works-snippet",
                    "Threat flow example",
                    HOW_IT_WORKS_SNIPPET,
                ),
                "EXAMPLE_CARDS": render_example_cards(),
                "DIAGRAM_EXAMPLES": render_diagram_examples(),
                "NEXT_STEPS_LINKS": render_next_steps(),
            },
        ),
        encoding="utf-8",
    )

    verify_site_output(output_dir)
    print(f"wrote {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
