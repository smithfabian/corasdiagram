# Treatment Diagrams

English sentence forms:

- `... is a treatment scenario.`
- `... treats ....`
- `... decreases the likelihood of ....`
- `... decreases the consequence of ....`

Canonical commands:

- `\treatmentscenario[...]`
- `\treats{treatmentscenario -> target}[treatment category=...]`
- plus `\initiates`, `\leadsto`, and `\impacts` when the treated threat or risk chain is shown

## Concise example

```latex
\begin{corastreatmentdiagram}
  \vulnerability[id=old_av]{Virus protection not up to date}
  \treatmentscenario[id=update]{Implement new routines for updating virus protection}
  \treats{update -> old_av}[treatment category=reduce-likelihood]
\end{corastreatmentdiagram}
```

Full example:

- [Source](../assets/generated/examples/corasdiagram-treatment-diagram.tex)
- [PDF](../assets/generated/examples/corasdiagram-treatment-diagram.pdf)
