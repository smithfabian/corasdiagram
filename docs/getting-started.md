# Getting Started

## Installation

Compile from the repository root with:

```bash
TEXINPUTS=tex/latex//: latexmk -pdf -interaction=nonstopmode -halt-on-error \
  examples/corasdiagram-minimal.tex
```

For a user-level TEXMF install, copy `tex/latex/corasdiagram/` to:

```text
~/texmf/tex/latex/corasdiagram/
```

Supported engines:

- `pdflatex`
- `lualatex`

## Minimal semantic-first example

```latex
\documentclass{article}
\usepackage{corasdiagram}

\begin{document}

\begin{corasassetdiagram}[x=1cm,y=1cm,asset columns=2]
  \party[id=company]{Company}
  \asset(direct)[id=availability]{Availability of server}
  \asset(indirect)[id=reputation]{Company's reputation}

  \assigns{company -> availability}[asset value=critical]
  \assigns{company -> reputation}
  \harms{availability -> reputation}
\end{corasassetdiagram}

\end{document}
```

Downloads:

- [Minimal example source](assets/generated/examples/corasdiagram-minimal.tex)
- [Minimal example PDF](assets/generated/examples/corasdiagram-minimal.pdf)

## Local documentation builds

Build all tracked examples:

```bash
(cd examples && TEXINPUTS=../tex/latex//: \
  for tex in *.tex; do
    latexmk -pdf -interaction=nonstopmode -halt-on-error "$tex"
  done)
```

Build the manual:

```bash
(cd manual && TEXINPUTS=../tex/latex//: latexmk -pdf -interaction=nonstopmode -halt-on-error corasdiagram-doc.tex)
```

Build the docs site:

```bash
python3 -m pip install mkdocs-material
python3 tools/stage_mkdocs_assets.py --doc-pdf manual/corasdiagram-doc.pdf
python3 -m mkdocs build
```
