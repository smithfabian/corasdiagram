# Contributing to `corasdiagram`

## Project Workflow

This repository keeps the LaTeX package, documentation, examples, regression
tests, generated package assets, and release tooling together.

Normal lifecycle of a change:

1. Create a focused branch and make the package, docs, examples, and tests
   changes together.
2. Run the local checks that match the kind of change you made.
3. Open a pull request with a short motivation and the verification you ran.
4. Merge to `main` when the change is ready.
5. Let the `Pages` workflow publish the documentation site from `main` when the
   merged change affects the published docs/examples.
6. For a versioned release, update [`VERSION`](VERSION) and
   [`tex/latex/corasdiagram/corasdiagram-version.tex`](tex/latex/corasdiagram/corasdiagram-version.tex)
   together, update [`CHANGELOG.md`](CHANGELOG.md), keep the
   `\ProvidesPackage` date in
   [`tex/latex/corasdiagram/corasdiagram.sty`](tex/latex/corasdiagram/corasdiagram.sty)
   aligned with that release date, push a matching tag `v<version>`, and
   approve the `ctan-release` environment when you want the CTAN upload to
   continue.

Workflow boundaries:

- `CI` validates pull requests and pushes to `main`/`master`.
- `Pages` deploys the static documentation site from `main`.
- `Release` runs only for pushed tags matching `v*`.
- The package is now live on [CTAN](https://ctan.org/pkg/corasdiagram), so
  later tagged releases can continue through the gated release workflow.

## Canonical Sources and Generated Files

Repository-managed sources of truth:

- [`VERSION`](VERSION): canonical repository release number
- [`tex/latex/corasdiagram/corasdiagram-version.tex`](tex/latex/corasdiagram/corasdiagram-version.tex):
  TeX runtime mirror of `VERSION`
- [`tex/latex/corasdiagram/corasdiagram.sty`](tex/latex/corasdiagram/corasdiagram.sty):
  carries the LaTeX package header date that must match the current release
  date in [`CHANGELOG.md`](CHANGELOG.md)
- [`assets/icons-src/`](assets/icons-src): canonical icon sources
- [`NOTICE`](NOTICE): provenance and upstream MIT notice for the vendored icon
  sources
- [`ctan/metadata.json`](ctan/metadata.json): committed CTAN package metadata
- [`tests/corasdiagram/snapshots/`](tests/corasdiagram/snapshots): committed
  visual regression baselines

Generated or disposable outputs:

- [`tex/latex/corasdiagram/icons/`](tex/latex/corasdiagram/icons): generated
  runtime icon assets built from `assets/icons-src/`
- `dist/`: release bundles and static site output
- local TeX build products such as `.aux`, `.log`, generated PDFs, and
  temporary rasterized images
- local scratch output under `build/`

The CTAN release bundle is the exception: it intentionally includes the
compiled PDFs for the canonical examples under `doc/examples/`, alongside the
example `.tex` sources, plus the top-level [`LICENSE`](LICENSE) and
[`NOTICE`](NOTICE) files.

Do not edit generated runtime icons by hand. Rebuild them from
[`assets/icons-src/`](assets/icons-src) when the source icons change.

## Prerequisites

Local development expects:

- Python 3
- `pdflatex`
- `lualatex`
- `latexmk`
- `pdftoppm` for rasterized screenshot generation
- `cairosvg` only when rebuilding generated icon PDFs from the source SVG files
- `actionlint` when editing GitHub Actions workflows

## Local Checks

### Build the package docs and examples

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
(cd docs && TEXINPUTS=../tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error corasdiagram-doc.tex)
```

Build with LuaLaTeX:

```bash
TEXINPUTS=tex/latex//: TEXMFVAR=/tmp/corasdiagram-texmf TEXMFCACHE=/tmp/corasdiagram-texmf \
  lualatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-minimal.tex
```

### Run semantic and visual regressions

Run the semantic failure fixtures:

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

### Rebuild assets and use editing tools

Rebuild generated runtime icons from the canonical SVG sources:

```bash
python3 tools/build_coras_icons.py
```

Run the local browser-based anchor editor:

```bash
python3 tools/coras_anchor_editor.py
```

Smoke-test the parser/writer logic for the anchor editor:

```bash
python3 -m unittest tests/test_coras_anchor_editor.py
```

### Check packaging and release helpers

Verify the versioning story:

```bash
python3 tools/check_release_tag.py
```

Build the manual and the canonical example PDFs before assembling the release
bundle:

```bash
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-minimal.tex
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-demo.tex
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-high-level-analysis-table.tex
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-website-examples.tex
```

Then build the CTAN release bundle:

```bash
python3 tools/build_release.py --doc-pdf docs/corasdiagram-doc.pdf
```

Optionally validate the rebuilt archive against the CTAN API before approving
or manually uploading it:

```bash
python3 tools/upload_ctan.py \
  --archive "dist/corasdiagram-$(cat VERSION).zip" \
  --uploader "Fabian Robert Smith" \
  --email "fabian.smith@me.com" \
  --update false \
  --validate-only
```

Generate the static documentation site after compiling the examples and manual:

```bash
python3 tools/build_site.py \
  --docs-pdf docs/corasdiagram-doc.pdf \
  --demo-pdf examples/corasdiagram-demo.pdf \
  --minimal-pdf examples/corasdiagram-minimal.pdf \
  --website-examples-pdf examples/corasdiagram-website-examples.pdf \
  --analysis-table-pdf examples/corasdiagram-high-level-analysis-table.pdf
```

If you edit workflow files, lint them:

```bash
actionlint .github/workflows/ci.yml .github/workflows/pages.yml .github/workflows/release.yml
```

## Change Checklist by Change Type

### Public API or notation change

- update the package source, examples, and the manual together
- update [`README.md`](README.md) if the user-facing setup, supported API, or
  workflow summary changed
- update [`CHANGELOG.md`](CHANGELOG.md) for public-facing behavior changes
- run the relevant TeX builds plus semantic and visual checks
- add or update negative semantic fixtures if the change affects validation

### Visual or layout change

- run `python3 tools/check_visual_regressions.py`
- update committed baselines in the same change with `--update`
- keep snapshot changes scoped to the intentional visual difference
- recheck demo/manual/example output after updating baselines

### Icon or source asset change

- edit only files in `assets/icons-src/`
- rebuild the generated runtime icons with `tools/build_coras_icons.py`
- verify both color and `iconset=bw` outputs still compile cleanly
- update snapshots, examples, and docs if the rendered symbols changed

### Docs-only change

- update the relevant repo docs and/or the package manual
- build the manual if `docs/corasdiagram-doc.tex` changed
- keep repo-facing contributor/runbook material in `README.md` and
  `CONTRIBUTING.md`, not in the package manual

### Release or version change

- update [`VERSION`](VERSION)
- update
  [`tex/latex/corasdiagram/corasdiagram-version.tex`](tex/latex/corasdiagram/corasdiagram-version.tex)
  to the same value
- update [`CHANGELOG.md`](CHANGELOG.md)
- update the `\ProvidesPackage` date in
  [`tex/latex/corasdiagram/corasdiagram.sty`](tex/latex/corasdiagram/corasdiagram.sty)
  to match the release date
- run `python3 tools/check_release_tag.py`
- create and push the matching tag `v<version>`
- approve the `ctan-release` environment when you want the CTAN upload job to
  proceed

## Versioning and Releases

The repository uses one canonical versioning story:

- `VERSION` is the canonical repository release number
- `corasdiagram-version.tex` is the TeX runtime mirror and must match `VERSION`
- the `\ProvidesPackage` date in `corasdiagram.sty` must match the current
  dated `CHANGELOG.md` release entry
- release tags must be `v<version>`
- the `Release` workflow verifies the version/tag story and package header date
  before building or publishing anything
- CTAN upload versioning is derived as `<VERSION> <release-date>`, where the
  release date comes from the matching dated entry in [`CHANGELOG.md`](CHANGELOG.md)

Release behavior:

- a pushed `v*` tag builds the release archive and GitHub release assets
- the same tag starts the gated CTAN publication job
- the `ctan-release` environment contains `CTAN_UPLOADER_NAME` and
  `CTAN_UPLOADER_EMAIL`
- the `ctan-release` environment requires review by `smithfabian`, so the CTAN
  upload job cannot read those values or continue without approval
- the package is now published at [ctan.org/pkg/corasdiagram](https://ctan.org/pkg/corasdiagram)
- [`ctan/metadata.json`](ctan/metadata.json) keeps the committed CTAN package
  metadata, including the selected topics (`diagram`, `pgf-tikz`) and the
  announcement URL used for manual/reference purposes
- the current API-based uploader submits only CTAN fields that the CTAN upload
  API supports, so the committed `announce` URL is not sent automatically
- non-empty CTAN URL-role fields must be unique across `home`, `repository`,
  `development`, `bugtracker`, `support`, and `announce`

Pages behavior:

- Pages deployment is handled by the dedicated `Pages` workflow
- pushes to `main` can update the documentation site
- tagged releases do not deploy Pages directly

## When to Update Docs, Examples, and Tests

Update the docs/examples/tests in the same change when:

- public behavior changes: update the manual, examples, and relevant README
  sections
- semantic validation changes: add or update negative tests
- visual rendering changes: refresh committed visual baselines
- icon changes: update source icons, generated runtime icons, and any examples
  or snapshots that show them
- release workflow or contribution workflow changes: update both
  [`README.md`](README.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md)

## Coding and Documentation Style

- Prefer the semantic CORAS macros in docs and examples.
- Keep low-level primitives available for compatibility unless a deprecation is
  explicitly planned and documented.
- Default to ASCII in source files unless there is a clear reason not to.
- Keep CI-friendly commands shell-friendly and reproducible from the repository
  root.
- Do not rely on undocumented local steps for releases, snapshots, or icon
  generation; if a workflow matters, document it here or in the relevant script
  header/docstring.

## Pull Requests

Pull requests should:

1. stay focused on one change or one closely related set of changes
2. explain the motivation briefly
3. list the verification that was actually run
4. update docs/examples/tests together when public behavior changed
5. update [`CHANGELOG.md`](CHANGELOG.md) when the public API or release-visible
   behavior changed
