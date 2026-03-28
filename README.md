# corasdiagram

`corasdiagram` is a LaTeX package for authoring CORAS diagrams with reusable
notation macros, package-managed icons, semantic diagram environments, and
high-level analysis tables.

The package currently supports the five basic CORAS diagram families:

- asset diagrams
- threat diagrams
- risk diagrams
- treatment diagrams
- treatment overview diagrams

It also supports high-level analysis risk tables with CORAS header icons.

For narrow layouts such as a side-by-side `minipage` in Overleaf, the high-level
analysis table accepts `icon scale=<factor>` to shrink the header icon groups,
for example `icon scale=0.6`.

The supported TeX engines are `pdflatex` and `lualatex`.

## Author and Contact

- Author and maintainer: Fabian Robert Smith
- Contact email: <fabian.smith@me.com>
- Repository and issue tracker:
  [github.com/smithfabian/corasdiagram](https://github.com/smithfabian/corasdiagram)
  ([issues](https://github.com/smithfabian/corasdiagram/issues))

## How the Project Works

This repository keeps the package source, documentation, regression tests, and
release tooling in one place.

Canonical sources of truth:

- [`VERSION`](VERSION) is the canonical repository release number.
- [`tex/latex/corasdiagram/corasdiagram-version.tex`](tex/latex/corasdiagram/corasdiagram-version.tex)
  is the TeX runtime mirror of that version and must match `VERSION`.
- the `\ProvidesPackage` date in
  [`tex/latex/corasdiagram/corasdiagram.sty`](tex/latex/corasdiagram/corasdiagram.sty)
  must match the current release date in [`CHANGELOG.md`](CHANGELOG.md)
- [`assets/icons-src/`](assets/icons-src) holds the canonical icon sources.
- [`NOTICE`](NOTICE) records provenance and the upstream MIT notice for the
  vendored icon sources.
- [`tex/latex/corasdiagram/icons/`](tex/latex/corasdiagram/icons) holds the
  generated runtime icon assets used by the package.
- [`tests/corasdiagram/snapshots/`](tests/corasdiagram/snapshots) holds the
  committed visual regression baselines.
- [`ctan/metadata.json`](ctan/metadata.json) holds the committed CTAN metadata
  used by the release tooling.

Workflow map:

- normal development happens on branches and pull requests
- merges to `main` trigger CI and deploy the documentation site through the
  dedicated `Pages` workflow
- pushed version tags matching `vX.Y.Z` trigger the `Release` workflow
- the release workflow verifies that the tag matches `VERSION` and that the
  package header date matches the current `CHANGELOG.md` release date, builds
  the release archive, publishes the GitHub release assets, and waits at the
  `ctan-release` environment before any CTAN upload can continue

For the full contributor runbook, change checklists, and release procedure, see
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Repository Layout

The package source lives in [`tex/latex/corasdiagram/`](tex/latex/corasdiagram),
examples live in [`examples/`](examples), the manual source lives in
[`docs/`](docs), semantic regression tests live in
[`tests/corasdiagram/`](tests/corasdiagram), and committed visual baselines
live in [`tests/corasdiagram/snapshots/`](tests/corasdiagram/snapshots). CTAN
metadata lives in [`ctan/`](ctan), and the helper scripts used by CI, Pages,
releases, and local development live in [`tools/`](tools).

## Installation

For local development inside this repository, compile with:

```bash
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-minimal.tex
```

For a user-level TEXMF installation from a repository checkout, copy
[`tex/latex/corasdiagram/`](tex/latex/corasdiagram)
to `~/texmf/tex/latex/corasdiagram/` and refresh the TeX filename database if
your distribution requires it.

The release workflow also assembles a CTAN-friendly distribution bundle with
runtime files flattened under `tex/`, documentation under `doc/`, and the
top-level metadata files such as [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
If you are installing from that bundle manually, copy the contents of `tex/`
into `~/texmf/tex/latex/corasdiagram/`. Once the package is published to CTAN
or TeX Live, installation can happen through the normal package manager for the
TeX distribution.

## Using In Your Own Project

The package can be used directly in both Overleaf projects and ordinary local
LaTeX projects by copying the package file together with its icon assets.

### Overleaf

Upload these from the repository:

- [`tex/latex/corasdiagram/corasdiagram.sty`](tex/latex/corasdiagram/corasdiagram.sty)
- the full [`tex/latex/corasdiagram/icons/`](tex/latex/corasdiagram/icons) directory

The simplest Overleaf layout is:

```text
main.tex
corasdiagram.sty
icons/
  corasdiagram-asset.pdf
  corasdiagram-stakeholder.pdf
  corasdiagram-risk.pdf
  ...
```

Then load the package normally:

```latex
\usepackage{corasdiagram}
```

This works because the package resolves the default icon path relative to the
location of `corasdiagram.sty`.

If you prefer to keep the package in a subfolder, keep the `icons/` directory
beside the `.sty` file, for example:

```text
main.tex
corasdiagram/
  corasdiagram.sty
  icons/
    corasdiagram-asset.pdf
    corasdiagram-stakeholder.pdf
    ...
```

and load it with:

```latex
\usepackage{corasdiagram/corasdiagram}
```

If your icon directory is somewhere else, set it explicitly:

```latex
\usepackage[icons-path=coras-assets/icons]{corasdiagram}
```

### Local LaTeX Projects

For a normal local project outside this repository, copy the same files into
your project tree:

```text
my-project/
  main.tex
  corasdiagram.sty
  icons/
```

and load the package with:

```latex
\usepackage{corasdiagram}
```

You can also keep the package in a subdirectory and point LaTeX at it in the
usual way, either by using a TEXMF tree or by loading the package through its
relative path:

```latex
\usepackage{vendor/corasdiagram/corasdiagram}
```

In that case, keep the `icons/` folder next to the `.sty` file or pass an
explicit `icons-path=...`.

## Minimal Example

```latex
\documentclass{article}
\usepackage{corasdiagram}

\begin{document}

\begin{corasassetdiagram}[x=1cm,y=1cm]
  \corasstakeholder[
    name=stakeholder,
    scope=asset-scope,
    order=1,
    title={Stakeholder}
  ]
  \corasasset[
    name=asset,
    scope=asset-scope,
    order=1,
    title={Asset}
  ]
  \corasindirectasset[
    name=indirect,
    scope=asset-scope,
    order=2,
    title={Indirect\\Asset}
  ]
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
```

## Screenshots

The release workflow publishes the manual PDF and rendered diagram screenshots
to GitHub Pages and the release artifacts. The committed source tree keeps only
the package sources and example `.tex` files.

## Public API

The current supported semantic package API is:

- package options: `iconset`, `icons-path`
- common node keys such as `perspective=before|before-after|after`
- diagram environments:
  `corasassetdiagram`, `corasthreatdiagram`, `corasriskdiagram`,
  `corastreatmentdiagram`, `corastreatmentoverviewdiagram`
- high-level analysis table environments:
  `corashighlevelanalysistable`, `corashighlevelrisktable`
- concept node macros such as `\corasasset`, `\corasindirectasset`, `\corasstakeholder`,
  `\corasrisk`, `\corastreatment`, and the threat/vulnerability/scenario
  family
- semantic edge macros such as `\corascauses`, `\corasrelates`,
  `\corasconcerns`, `\corasassociates`, and `\corastreats`
- table row macros:
  `\corashighlevelanalysisrow`, `\corashighlevelriskrow`
- `\corasscope`, including `kind=asset-scope` and the stakeholder corner
  compartment options

The `perspective` key applies to the public node macros and mounted-icon body
nodes. `before` uses the base icon, `before-after` uses the outlined variant,
and `after` uses the shaded variant.

```latex
\corasasset[
  name=baseline,
  title={Asset},
  perspective=before
]
\corasindirectasset[
  name=transition,
  title={Indirect\\Asset},
  perspective=before-after
]
\corastreatment[
  name=target,
  title={Treatment},
  perspective=after
]
```

Low-level primitives such as `\corasnode`, `\corasedge`, and `\corascontainer`
remain available for compatibility, but they are documented as advanced
interfaces rather than the preferred author-facing API.

## Documentation

The source for the package manual is
[`docs/corasdiagram-doc.tex`](docs/corasdiagram-doc.tex).
Compile it locally with:

```bash
(cd docs && TEXINPUTS=../tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error corasdiagram-doc.tex)
```

The workflows publish the manual PDF and rendered example screenshots as CI
artifacts, and the dedicated `Pages` workflow publishes the documentation site
to GitHub Pages.

## Release and Deployment

The repository uses separate workflows for CI, Pages, and tagged releases:

- `CI` validates changes on pull requests and branch pushes
- `Pages` builds and deploys the documentation site from `main`
- `Release` runs only for pushed `v*` tags and handles versioned release assets
  plus the gated CTAN publication step

The `ctan-release` environment is the approval boundary for automated CTAN
updates. The first CTAN submission is still expected to be done manually. For
the exact release, approval, and versioning procedure, see
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Regression Tests

Run the semantic failure fixtures with:

```bash
python3 tools/check_negative_tests.py --engine pdflatex
```

Run the visual regression suite with:

```bash
python3 tools/check_visual_regressions.py
```

If a notation or layout change is intentional, regenerate the baselines in the
same change with:

```bash
python3 tools/check_visual_regressions.py --update
```

## Anchor Editor

For interactive tuning of the symbol-table anchor maps, run:

```bash
python3 tools/coras_anchor_editor.py
```

This starts a local browser-based editor that lets you drag the directional
anchors for `asset`, `stakeholder`, the threat variants, and `vulnerability`,
then save the values directly back into
[`tex/latex/corasdiagram/corasdiagram.sty`](tex/latex/corasdiagram/corasdiagram.sty).

The app also shows read-only previews for `scenario`, `treatment`, `incident`,
and `risk`, using locally rebuilt images from the anchor regression fixture.

## Contributing

Contribution guidelines are in [`CONTRIBUTING.md`](CONTRIBUTING.md).
Please open issues for notation bugs, layout regressions, documentation gaps,
or feature ideas. The public issue labels include `good first issue`,
`help wanted`, `documentation`, `notation`, `layout`, and `ci`.

## License

This project is licensed under the MIT license. See [`LICENSE`](LICENSE).
The vendored CORAS icon sources also carry upstream MIT attribution and
provenance in [`NOTICE`](NOTICE).
