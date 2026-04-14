# Treatment Overview Mode

Treatment overview is expressed with `corastreatmentdiagram[mode=overview]`.

Use this mode when the document should attach treatment scenarios directly to risks instead of showing the full threat or incident chain.

## Concise example

```latex
\begin{corastreatmentdiagram}[mode=overview]
  \risk[id=r1,risk ref=R1,risk level=high]{Credential theft}
  \treatmentscenario[id=t1]{Hardware keys}
  \treats{t1 -> r1}[treatment category=reduce-likelihood]
\end{corastreatmentdiagram}
```

Full example:

- [Source](../assets/generated/examples/corasdiagram-treatment-overview-diagram.tex)
- [PDF](../assets/generated/examples/corasdiagram-treatment-overview-diagram.pdf)
