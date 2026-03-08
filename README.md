# corasdiagram

`corasdiagram` is a LaTeX package for authoring CORAS diagrams with reusable
notation macros, package-managed icons, and semantic diagram environments.

The package currently supports the five basic CORAS diagram families:

- asset diagrams
- threat diagrams
- risk diagrams
- treatment diagrams
- treatment overview diagrams

Version `0.1.0` is the first open-source release target. The supported TeX
engines are `pdflatex` and `lualatex`.

## Repository Layout

The package source lives in [`tex/latex/corasdiagram/`](tex/latex/corasdiagram),
examples live in [`examples/`](examples), the manual source lives in
[`docs/`](docs), and semantic regression tests live in
[`tests/corasdiagram/`](tests/corasdiagram).

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
  \corasasset[
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
- diagram environments:
  `corasassetdiagram`, `corasthreatdiagram`, `corasriskdiagram`,
  `corastreatmentdiagram`, `corastreatmentoverviewdiagram`
- concept node macros such as `\corasasset`, `\corasstakeholder`,
  `\corasrisk`, `\corastreatment`, and the threat/vulnerability/scenario
  family
- semantic edge macros such as `\corascauses`, `\corasrelates`,
  `\corasconcerns`, `\corasassociates`, and `\corastreats`
- `\corasscope`, including `kind=asset-scope` and the stakeholder corner
  compartment options

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

## Contributing

Contribution guidelines are in [`CONTRIBUTING.md`](CONTRIBUTING.md).
Please open issues for notation bugs, layout regressions, documentation gaps,
or feature ideas. The public issue labels include `good first issue`,
`help wanted`, `documentation`, `notation`, `layout`, and `ci`.

## License

This project is licensed under the MIT license. See [`LICENSE`](LICENSE).
