# Asset Diagrams

English sentence forms:

- `... is a party.`
- `... is a direct asset.`
- `... is an indirect asset.`
- `... assigns value to ....`
- `... assigns the value ... to ....`
- `Harm to ... may result in harm to ....`

Canonical commands:

- `\party[...]`
- `\asset(direct)[...]`
- `\asset(indirect)[...]`
- `\assigns{party -> asset}[asset value=...]`
- `\harms{asset -> asset}`

## Concise example

```latex
\begin{corasassetdiagram}[asset columns=3]
  \party[id=company]{Company}
  \asset(direct)[id=availability]{Availability of server}
  \asset(indirect)[id=reputation]{Company's reputation}

  \assigns{company -> availability}[asset value=critical]
  \assigns{company -> reputation}
  \harms{availability -> reputation}
\end{corasassetdiagram}
```

Full example:

- [Source](../assets/generated/examples/corasdiagram-asset-diagram.tex)
- [PDF](../assets/generated/examples/corasdiagram-asset-diagram.pdf)
