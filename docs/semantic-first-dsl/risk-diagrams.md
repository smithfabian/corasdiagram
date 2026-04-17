# Risk Diagrams

English sentence forms:

- `Risk ... occurs with risk level ....`
- `... initiates ....`
- `... impacts ....`

Canonical commands:

- `\risk[...]`
- `\initiates{source -> risk}`
- `\impacts{risk -> asset}[consequence=...]`

## Concise example

```latex
\begin{corasriskdiagram}
  \threat(deliberate)[id=hacker]{Hacker}
  \risk[id=r1,risk ref=R1,risk level=unacceptable]{Disclosure of data}
  \asset(direct)[id=privacy]{Data privacy}

  \initiates{hacker -> r1}
  \impacts{r1 -> privacy}
\end{corasriskdiagram}
```

Full example:

- [Source](../assets/generated/examples/corasdiagram-risk-diagram.tex)
- [PDF](../assets/generated/examples/corasdiagram-risk-diagram.pdf)
