# Threat Diagrams

English sentence forms:

- `... is a deliberate human threat.`
- `... is an accidental human threat.`
- `... is a non-human threat.`
- `... is a vulnerability.`
- `Threat scenario ... occurs with likelihood ....`
- `Unwanted incident ... occurs with likelihood ....`
- `... exploits vulnerability ... to initiate ....`
- `... leads to ... with conditional likelihood ....`
- `... impacts ... with consequence ....`

Canonical commands:

- `\threat(deliberate|accidental|nonhuman)[...]`
- `\vulnerability[...]`
- `\threatscenario[...]`
- `\unwantedincident[...]`
- `\initiates{source -> target}[vulnerability=...]`
- `\leadsto{source -> target}[conditional likelihood=...]`
- `\impacts{incident -> asset}[consequence=...]`

## Concise example

```latex
\begin{corasthreatdiagram}
  \threat(nonhuman)[id=virus]{Computer virus}
  \vulnerability[id=old_av]{Virus protection not up to date}
  \threatscenario[id=infection,likelihood=possible]{Server is infected}
  \unwantedincident[id=down,likelihood=unlikely]{Server goes down}
  \asset(direct)[id=availability]{Availability of server}

  \initiates{virus -> infection}[vulnerability={old_av}]
  \leadsto{infection -> down}[conditional likelihood=0.2]
  \impacts{down -> availability}[consequence=high]
\end{corasthreatdiagram}
```

Full example:

- [Source](../assets/generated/examples/corasdiagram-threat-diagram.tex)
- [PDF](../assets/generated/examples/corasdiagram-threat-diagram.pdf)
