# Contributing to `corasdiagram`

## Prerequisites

Local development expects:

- Python 3
- `pdflatex`
- `lualatex`
- `latexmk`
- `pdftoppm` for screenshot generation
- `cairosvg` only if you need to rebuild icon PDFs from the source SVG files

## Local Checks

Build the minimal example:

```bash
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-minimal.tex
```

Build the full demo:

```bash
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-demo.tex
```

Build the manual:

```bash
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error docs/corasdiagram-doc.tex
```

Build with LuaLaTeX:

```bash
TEXINPUTS=tex/latex//: TEXMFVAR=/tmp/corasdiagram-texmf TEXMFCACHE=/tmp/corasdiagram-texmf \
  lualatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-minimal.tex
```

Run the semantic failure checks:

```bash
python3 tools/check_negative_tests.py --engine pdflatex
```

Run the visual regression checks:

```bash
python3 tools/check_visual_regressions.py
```

Regenerate committed snapshot baselines after an intentional notation or layout
change:

```bash
python3 tools/check_visual_regressions.py --update
```

Run the local browser-based anchor editor:

```bash
python3 tools/coras_anchor_editor.py
```

Smoke-test the parser/writer logic for the anchor editor:

```bash
python3 -m unittest tests/test_coras_anchor_editor.py
```

Build a release bundle after compiling the manual:

```bash
python3 tools/build_release.py --doc-pdf docs/corasdiagram-doc.pdf
```

Generate the static documentation site after compiling the examples and manual:

```bash
python3 tools/build_site.py \
  --docs-pdf docs/corasdiagram-doc.pdf \
  --demo-pdf examples/corasdiagram-demo.pdf \
  --minimal-pdf examples/corasdiagram-minimal.pdf
```

## CI, Release, and Pages

The repository uses two GitHub Actions workflows:

- `CI`: runs on pull requests, pushes to `main`/`master`, and manual dispatch
- `Release`: runs on manual dispatch and on pushed tags matching `v*`

Pages deployment is intentionally more restricted than release artifact
publication:

- the `github-pages` environment currently allows deployments only from the
  `main` branch
- a pushed version tag still builds the release bundle and GitHub release
  assets, but the Pages deploy job will be rejected unless the environment
  rules are changed

For contributors, that means:

- push a `v*` tag when you want to publish a versioned release
- run the `Release` workflow manually from `main` when you want to deploy the
  GitHub Pages site
- do not expect a tag push alone to update Pages under the current repository
  protection rules

## Coding and Documentation Style

- Prefer the current semantic CORAS macros in docs and examples.
- Keep low-level primitives available for compatibility unless a deprecation is
  explicitly planned and documented.
- Default to ASCII in source files unless there is a clear reason not to.
- Update examples and the manual when public behavior changes.
- Add or update semantic regression tests when notation validation changes.
- Update visual snapshot baselines in the same change when rendered notation or
  layout intentionally changes.
- Keep CI-friendly commands shell-friendly and reproducible from the repository
  root.

## Pull Requests

The expected workflow is:

1. Fork the repository.
2. Create a focused branch for the change.
3. Update source, docs, examples, and tests together.
4. Run the local checks that apply to the change.
5. Open a pull request with a concise description of the motivation and the
   verification you ran.

Pull requests that change the public API should also update
[`CHANGELOG.md`](CHANGELOG.md).
