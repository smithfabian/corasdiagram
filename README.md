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

Version `0.1.0` is the first open-source release target. The supported TeX
engines are `pdflatex` and `lualatex`.

## Repository Layout

The package source lives in [`tex/latex/corasdiagram/`](tex/latex/corasdiagram),
examples live in [`examples/`](examples), the manual source lives in
[`docs/`](docs), semantic regression tests live in
[`tests/corasdiagram/`](tests/corasdiagram), and committed visual baselines
live in [`tests/corasdiagram/snapshots/`](tests/corasdiagram/snapshots).

## Installation

For local development inside this repository, compile with:

```bash
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error examples/corasdiagram-minimal.tex
```

For a user-level TEXMF installation, copy
[`tex/latex/corasdiagram/`](tex/latex/corasdiagram)
to `~/texmf/tex/latex/corasdiagram/` and refresh the TeX filename database if
your distribution requires it.

The release workflow also assembles a CTAN-friendly distribution bundle. Once
the package is published to CTAN or TeX Live, installation can happen through
the normal package manager for the TeX distribution.

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
  asset.pdf
  stakeholder.pdf
  risk.pdf
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
    asset.pdf
    stakeholder.pdf
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

The supported `0.1.0` surface is the current semantic package API:

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
TEXINPUTS=tex/latex//: pdflatex -interaction=nonstopmode -halt-on-error docs/corasdiagram-doc.tex
```

The release workflow publishes the manual PDF and rendered example screenshots
as CI artifacts and as a GitHub Pages site.

## Release and Deployment

The repository has separate CI and release workflows:

- CI runs on pull requests, on pushes to `main`/`master`, and on manual
  dispatch.
- Release runs on manual dispatch and on version tags matching `v*`.

Important Pages deployment rule:

- The `github-pages` environment currently allows deployments only from the
  `main` branch.
- A tag push such as `v0.1.0` will still build the release artifacts and
  publish GitHub release assets, but the Pages deployment step will be rejected
  unless the environment protection rules are changed.

Current contributor guidance:

- Use a tag push to publish a versioned release.
- Use a manual `Release` workflow run from `main` when you want to deploy the
  GitHub Pages site.

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
