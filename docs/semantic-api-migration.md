# Semantic API Migration Guide

This guide is the canonical migration reference for the semantic-first CORAS
DSL. Use it together with the user-facing [Compatibility Guide](compatibility-guide.md)
and the semantic-first family pages in this documentation site.

## Canonical surface

The preferred API is now the semantic-first layer:

- Elements:
  - `\party`
  - `\asset(direct)` / `\asset(indirect)`
  - `\threat(deliberate|accidental|nonhuman)`
  - `\vulnerability`
  - `\threatscenario`
  - `\unwantedincident`
  - `\risk`
  - `\treatmentscenario`
- Relations:
  - `\assigns`
  - `\harms`
  - `\initiates`
  - `\leadsto`
  - `\impacts`
  - `\treats`

Treatment overview is now expressed with:

```latex
\begin{corastreatmentdiagram}[mode=overview]
  ...
\end{corastreatmentdiagram}
```

## Retained compatibility aliases

Only these older public shapes remain intentionally supported:

- `corastreatmentoverviewdiagram`
- `\asset[...]` as `\asset(direct)[...]`
- `\indirectasset[...]`
- `\scenario[...]`
- `\incident[...]`
- `\treatment[...]`
- `\cause{...}`
- `\impact{...}`
- `\relate{...}`
- `\concern{...}`
- `\treat{...}`
- `\associate{...}`
- `risk id`, `risk-id`, `riskid`

Everything else from the old public wrapper layer is removed and now errors
with a replacement message.

## Removed commands and keys

Removed commands now fail with explicit migration guidance:

- `\stakeholder` -> `\party`
- all legacy `\coras...` node wrappers -> semantic node commands
- all legacy `\coras...` edge wrappers -> semantic edge commands

Removed keys now fail with explicit migration guidance:

- node keys:
  - `meta`
  - `level`
  - `value`
  - `likelihood label`
- edge keys:
  - `via`
  - `probability`
  - `has_vulnerability`
- scope keys:
  - `stakeholder`
  - `stakeholder corner`
  - `stakeholder xsep`
  - `stakeholder ysep`
  - `stakeholder tikz`

## `\cause` migration rule

`\cause` is now a compatibility dispatcher, not a canonical command.

- It maps to `\initiates` when the full edge specification is valid only as an
  initiation relation.
- It maps to `\leadsto` when the full edge specification is valid only as a
  leads-to relation.
- It errors when the edge specification is valid as both, or as neither.

Use `\initiates` and `\leadsto` directly in new code.

## Before / after rewrites

### Asset diagram

Before:

```latex
\begin{corasassetdiagram}
  \asset[id=availability]{Availability of server}
  \indirectasset[id=reputation]{Company's reputation}
  \concern{company -> availability}[asset value=critical]
  \relate{availability -> reputation}
\end{corasassetdiagram}
```

After:

```latex
\begin{corasassetdiagram}
  \party[id=company]{Company}
  \asset(direct)[id=availability]{Availability of server}
  \asset(indirect)[id=reputation]{Company's reputation}
  \assigns{company -> availability}[asset value=critical]
  \harms{availability -> reputation}
\end{corasassetdiagram}
```

### Threat diagram

Before:

```latex
\begin{corasthreatdiagram}
  \threat(nonhuman)[id=virus]{Computer virus}
  \scenario[id=infection]{Server is infected}
  \incident[id=down]{Server goes down}
  \cause{virus -> infection}[vulnerability={Virus protection not up to date}]
  \cause{infection -> down}[conditional likelihood=0.2]
\end{corasthreatdiagram}
```

After:

```latex
\begin{corasthreatdiagram}
  \threat(nonhuman)[id=virus]{Computer virus}
  \threatscenario[id=infection]{Server is infected}
  \unwantedincident[id=down]{Server goes down}
  \initiates{virus -> infection}[vulnerability={Virus protection not up to date}]
  \leadsto{infection -> down}[conditional likelihood=0.2]
\end{corasthreatdiagram}
```

### Risk diagram

Before:

```latex
\begin{corasriskdiagram}
  \threat(deliberate)[id=hacker]{Hacker}
  \risk[id=r1,risk id=R1,risk level=unacceptable]{Disclosure of data}
  \impact{r1 -> privacy}
\end{corasriskdiagram}
```

After:

```latex
\begin{corasriskdiagram}
  \threat(deliberate)[id=hacker]{Hacker}
  \risk[id=r1,risk ref=R1,risk level=unacceptable]{Disclosure of data}
  \impacts{r1 -> privacy}
\end{corasriskdiagram}
```

### Treatment diagram

Before:

```latex
\begin{corastreatmentoverviewdiagram}
  \risk[id=r1,risk id=R1,risk level=unacceptable]{Credential theft}
  \treatment[id=t1]{Hardware keys}
  \treat{t1 -> r1}[treatment category={Reduce likelihood}]
\end{corastreatmentoverviewdiagram}
```

After:

```latex
\begin{corastreatmentdiagram}[mode=overview]
  \risk[id=r1,risk ref=R1,risk level=unacceptable]{Credential theft}
  \treatmentscenario[id=t1]{Hardware keys}
  \treats{t1 -> r1}[treatment category={Reduce likelihood}]
\end{corastreatmentdiagram}
```

## Release boundary

The migration boundary for the semantic-first release is:

- preferred surface: semantic-first commands and keys only
- compatibility surface: only the retained aliases listed above
- advanced public surface: `\junction`, `\corasscope`, `\corascontainer`,
  `\corasriskref`, `\corasnode`, `\corasedge`, and `\associate`

For release validation, run:

```bash
python3 tools/check_release_gate.py
```
