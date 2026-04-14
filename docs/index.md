# corasdiagram

`corasdiagram` is a semantic-first LaTeX package for CORAS asset, threat, risk, and treatment diagrams plus the high-level CORAS tables.

The preferred public API mirrors the formal English-prose semantics of the CORAS language:

- semantic node names such as `\party`, `\threatscenario`, `\unwantedincident`, and `\treatmentscenario`
- semantic relation names such as `\assigns`, `\harms`, `\initiates`, `\leadsto`, `\impacts`, and `\treats`
- treatment overview expressed with `corastreatmentdiagram[mode=overview]`

## Start here

- [Getting Started](getting-started.md): install, minimal example, and local build commands.
- [Semantic-First DSL](semantic-first-dsl/asset-diagrams.md): family-by-family canonical syntax.
- [Complete Examples](complete-examples.md): download the full example sources and PDFs for every diagram and table family.
- [Migration Guide](semantic-api-migration.md): move from the retained compatibility aliases to the canonical surface.
- [Manual PDF](manual-pdf.md): printable reference manual with full compileable examples.

## Diagram and table families

- Asset diagrams: `corasassetdiagram`
- Threat diagrams: `corasthreatdiagram`
- Risk diagrams: `corasriskdiagram`
- Treatment diagrams: `corastreatmentdiagram`
- Treatment overview: `corastreatmentdiagram[mode=overview]`
- Tables: `corashighlevelanalysistable` and `corashighlevelrisktable`
