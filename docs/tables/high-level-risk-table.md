# High-Level Risk Table

`corashighlevelrisktable` and `\corashighlevelriskrow` remain available as the high-level risk table naming variant. They are kept for compatibility and document readability.

## Example

```latex
\begin{corashighlevelrisktable}[caption={Documenting the high-level risks}]
  \corashighlevelriskrow
    {Hacker}
    {Exposes customer data}
    {Weak authentication controls}
\end{corashighlevelrisktable}
```

Full example:

- [Source](../assets/generated/examples/corasdiagram-high-level-risk-table.tex)
- [PDF](../assets/generated/examples/corasdiagram-high-level-risk-table.pdf)
