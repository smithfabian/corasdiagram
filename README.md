# corasdiagram

`corasdiagram` is a semantic-first LaTeX package for CORAS asset, threat, risk, and treatment diagrams plus the high-level CORAS tables.

## Documentation

- [Docs site](https://smithfabian.github.io/corasdiagram/)
- [Manual PDF](https://smithfabian.github.io/corasdiagram/assets/generated/manual/corasdiagram-doc.pdf)
- [Migration guide](docs/semantic-api-migration.md)
- [Changelog](CHANGELOG.md)

## Install and compile

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

See the full compilable example sources in [examples/](examples/) and the complete family coverage in the [docs site](https://smithfabian.github.io/corasdiagram/complete-examples/).
