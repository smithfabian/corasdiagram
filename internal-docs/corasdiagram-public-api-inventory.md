# CORAS Public API Inventory

This is the canonical inventory for the current `corasdiagram` public surface.
It is organized for keep/remove review rather than tutorial reading.

For migration guidance and before/after rewrites, see
[`docs/semantic-api-migration.md`](../docs/semantic-api-migration.md).

Status legend:

- `Preferred`: canonical semantic-first surface
- `Compatibility`: explicitly retained aliases
- `Advanced`: public structural helpers and low-level primitives

Review markers are intentionally neutral in this pass:

- `Pending`

## Command-by-Family Matrix

| Surface | Asset | Threat | Risk | Treatment | Overview mode | Tables | Status | Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `corasassetdiagram` | ✓ | - | - | - | - | - | Preferred | Pending |
| `corasthreatdiagram` | - | ✓ | - | - | - | - | Preferred | Pending |
| `corasriskdiagram` | - | - | ✓ | - | - | - | Preferred | Pending |
| `corastreatmentdiagram` | - | - | - | ✓ | ✓ | - | Preferred | Pending |
| `corastreatmentoverviewdiagram` | - | - | - | - | ✓ | - | Compatibility | Pending |
| `corashighlevelanalysistable` | - | - | - | - | - | ✓ | Preferred | Pending |
| `corashighlevelrisktable` | - | - | - | - | - | ✓ | Compatibility | Pending |
| `\party` | ✓ | - | - | - | - | - | Preferred | Pending |
| `\asset(direct|indirect)` | ✓ | ✓ | ✓ | ✓ | ✓ | - | Preferred | Pending |
| `\threat(deliberate|accidental|nonhuman)` | - | ✓ | ✓ | ✓ | - | - | Preferred | Pending |
| `\vulnerability` | - | ✓ | ✓ | ✓ | - | - | Preferred | Pending |
| `\threatscenario` | - | ✓ | ✓ | ✓ | - | - | Preferred | Pending |
| `\unwantedincident` | - | ✓ | - | ✓ | - | - | Preferred | Pending |
| `\risk` | - | - | ✓ | ✓ | ✓ | - | Preferred | Pending |
| `\treatmentscenario` | - | - | - | ✓ | ✓ | - | Preferred | Pending |
| `\assigns` | ✓ | - | - | - | - | - | Preferred | Pending |
| `\harms` | ✓ | - | - | - | - | - | Preferred | Pending |
| `\initiates` | - | ✓ | ✓ | ✓ | - | - | Preferred | Pending |
| `\leadsto` | - | ✓ | ✓ | ✓ | - | - | Preferred | Pending |
| `\impacts` | - | ✓ | ✓ | ✓ | ✓ | - | Preferred | Pending |
| `\treats` | - | - | - | ✓ | ✓ | - | Preferred | Pending |
| `\junction` | ✓ | ✓ | ✓ | ✓ | ✓ | - | Advanced | Pending |
| `\corasscope` | ✓ | - | - | - | - | - | Advanced | Pending |
| `\corascontainer` | ✓ | - | - | - | - | - | Advanced | Pending |
| `\corasriskref` | - | - | - | ✓ | ✓ | - | Advanced | Pending |
| `\corasnode` | ✓ | ✓ | ✓ | ✓ | ✓ | - | Advanced | Pending |
| `\corasedge` | ✓ | ✓ | ✓ | ✓ | ✓ | - | Advanced | Pending |

## Modern Replacement Matrix

| Old shape | Status | Canonical replacement | Notes | Review |
| --- | --- | --- | --- | --- |
| `corastreatmentoverviewdiagram` | Compatibility | `corastreatmentdiagram[mode=overview]` | Environment alias only | Pending |
| `\asset[...]` | Compatibility | `\asset(direct)[...]` | Direct-asset shorthand | Pending |
| `\indirectasset[...]` | Compatibility | `\asset(indirect)[...]` | Indirect-asset alias | Pending |
| `\scenario[...]` | Compatibility | `\threatscenario[...]` | Naming alias | Pending |
| `\incident[...]` | Compatibility | `\unwantedincident[...]` | Naming alias | Pending |
| `\treatment[...]` | Compatibility | `\treatmentscenario[...]` | Naming alias | Pending |
| `\cause{...}` | Compatibility | `\initiates{...}` or `\leadsto{...}` | Dispatcher, errors on mixed semantics | Pending |
| `\impact{...}` | Compatibility | `\impacts{...}` | Pure alias | Pending |
| `\relate{...}` | Compatibility | `\harms{...}` or `\impacts{...}` | Family-sensitive dispatcher | Pending |
| `\concern{...}` | Compatibility | `\assigns{...}` | Pure alias | Pending |
| `\treat{...}` | Compatibility | `\treats{...}` | Pure alias | Pending |
| `risk id`, `risk-id`, `riskid` | Compatibility | `risk ref` | Key aliases only | Pending |
| `\associate{...}` | Advanced | none | Kept unchanged as an advanced compatibility edge | Pending |

## Diagram Environments

| Name | Category | Status | Purpose | Key inputs/options | Example | Review |
| --- | --- | --- | --- | --- | --- | --- |
| `corasassetdiagram` | Diagram environment | Preferred | Asset, party, assignment, and harm diagrams | TikZ options plus `layout`, `min edge gap`, `asset columns` | `\begin{corasassetdiagram}[x=1cm,y=1cm]` | Pending |
| `corasthreatdiagram` | Diagram environment | Preferred | Threat, vulnerability, scenario, incident, and asset diagrams | TikZ options plus `layout`, `min edge gap` | `\begin{corasthreatdiagram}[min edge gap=10mm]` | Pending |
| `corasriskdiagram` | Diagram environment | Preferred | Risk diagrams and compact risk views | TikZ options plus `layout`, `min edge gap` | `\begin{corasriskdiagram}` | Pending |
| `corastreatmentdiagram` | Diagram environment | Preferred | Treatment diagrams and overview mode | TikZ options plus `layout`, `min edge gap`, `mode` | `\begin{corastreatmentdiagram}[mode=overview]` | Pending |
| `corastreatmentoverviewdiagram` | Diagram environment | Compatibility | Compatibility alias for treatment overview mode | Same as treatment diagram | `\begin{corastreatmentoverviewdiagram}` | Pending |

## Table Environments and Row Macros

| Name | Category | Status | Purpose | Review |
| --- | --- | --- | --- | --- |
| `corashighlevelanalysistable` | Table environment | Preferred | High-level analysis table | Pending |
| `corashighlevelrisktable` | Table environment | Compatibility | Alias of analysis table | Pending |
| `\corashighlevelanalysisrow` | Table row macro | Preferred | Canonical analysis row macro | Pending |
| `\corashighlevelriskrow` | Table row macro | Compatibility | Alias of analysis row macro | Pending |

## Preferred Semantic Commands

### Node Commands

| Name/syntax | Category | Applies to | Purpose | Overlap/replacement | Review |
| --- | --- | --- | --- | --- | --- |
| `\party[...]` | Typed node | Asset | Party node | Replaces `\stakeholder` | Pending |
| `\asset(direct)[...]` | Typed node | All asset-accepting families | Direct asset node | Direct form of `\asset[...]` | Pending |
| `\asset(indirect)[...]` | Typed node | All asset-accepting families | Indirect asset node | Replaces `\indirectasset[...]` | Pending |
| `\threat(deliberate|accidental|nonhuman)[...]` | Typed node | Threat, risk, treatment | Threat source node | No planned replacement | Pending |
| `\vulnerability[...]` | Typed node | Threat, risk, treatment | Vulnerability node | No planned replacement | Pending |
| `\threatscenario[...]` | Typed node | Threat, risk, treatment | Threat scenario node | Replaces `\scenario[...]` | Pending |
| `\unwantedincident[...]` | Typed node | Threat, treatment | Unwanted incident node | Replaces `\incident[...]` | Pending |
| `\risk[...]` | Typed node | Risk, treatment, overview mode | Risk node | No planned replacement | Pending |
| `\treatmentscenario[...]` | Typed node | Treatment, overview mode | Treatment scenario node | Replaces `\treatment[...]` | Pending |

### Relation Commands

| Name/syntax | Category | Applies to | Purpose | Overlap/replacement | Review |
| --- | --- | --- | --- | --- | --- |
| `\assigns{party -> asset}[asset value=...]` | Typed edge | Asset | Party assigns value to asset | Replaces `\concern` | Pending |
| `\harms{asset -> asset}` | Typed edge | Asset | Harm-to-harm relation | Replaces asset use of `\relate` | Pending |
| `\initiates{source -> target}[vulnerability=...]` | Typed edge | Threat, risk, treatment | Initiation relation | Splits generic `\cause` | Pending |
| `\leadsto{source -> target}[conditional likelihood=...]` | Typed edge | Threat, risk, treatment | Follow-on causal relation | Splits generic `\cause` | Pending |
| `\impacts{incident|risk -> asset}[consequence=...]` | Typed edge | Threat, risk, treatment, overview mode | Asset-impact relation | Replaces `\impact`; also non-asset `\relate` | Pending |
| `\treats{treatmentscenario -> target}[treatment category=...]` | Typed edge | Treatment, overview mode | Treatment relation | Replaces `\treat` | Pending |

## Compatibility Layer

| Name | Category | Purpose | Notes | Review |
| --- | --- | --- | --- | --- |
| `\asset[...]` | Compatibility node alias | Direct asset shorthand | Same as `\asset(direct)[...]` | Pending |
| `\indirectasset[...]` | Compatibility node alias | Indirect asset shorthand | Same as `\asset(indirect)[...]` | Pending |
| `\scenario[...]` | Compatibility node alias | Threat scenario alias | Same as `\threatscenario[...]` | Pending |
| `\incident[...]` | Compatibility node alias | Unwanted incident alias | Same as `\unwantedincident[...]` | Pending |
| `\treatment[...]` | Compatibility node alias | Treatment scenario alias | Same as `\treatmentscenario[...]` | Pending |
| `\cause{...}` | Compatibility edge alias | Causal dispatcher | Resolves to `\initiates` or `\leadsto` | Pending |
| `\impact{...}` | Compatibility edge alias | Impact alias | Same as `\impacts` | Pending |
| `\relate{...}` | Compatibility edge alias | Family-sensitive relation alias | Asset => `\harms`, otherwise `\impacts` | Pending |
| `\concern{...}` | Compatibility edge alias | Assignment alias | Same as `\assigns` | Pending |
| `\treat{...}` | Compatibility edge alias | Treatment alias | Same as `\treats` | Pending |
| `risk id`, `risk-id`, `riskid` | Compatibility key aliases | Alternate spellings | Aliases of `risk ref` | Pending |

Removed and no longer public in the compatibility layer:

- `\stakeholder`
- all legacy `\coras...` node wrappers
- all legacy `\coras...` edge wrappers
- node keys `meta`, `level`, `value`, `likelihood label`
- edge keys `via`, `probability`, `has_vulnerability`
- scope keys `stakeholder`, `stakeholder corner`, `stakeholder xsep`, `stakeholder ysep`, `stakeholder tikz`

## Advanced Structural Layer

| Name | Category | Purpose | Notes | Review |
| --- | --- | --- | --- | --- |
| `\junction[...]` | Structural helper | Explicit fan-in or fan-out node | Public but not first-line semantic vocabulary | Pending |
| `\corasscope[...]` | Scope helper | Named scope/container and asset-scope party compartment | Asset diagrams only | Pending |
| `\corascontainer[...]` | Scope helper | Alias of `\corasscope` | Advanced alias retained | Pending |
| `\corasriskref[...]` | Reference helper | Free-standing risk reference tag | Treatment-oriented diagrams only | Pending |
| `\corasnode[...]` | Low-level primitive | Raw node construction | Use only when semantic commands cannot express the shape | Pending |
| `\corasedge[...]` | Low-level primitive | Raw edge construction | Use only when semantic commands cannot express the edge | Pending |
| `\associate{...}` | Advanced edge alias | Advanced association edge | Kept unchanged | Pending |

## Public Key Inventory

### Common Node Keys

| Key | Status | Applies to | Purpose | Review |
| --- | --- | --- | --- | --- |
| `id` | Preferred | Typed nodes | Stable public identifier | Pending |
| `at` | Preferred | Typed nodes | Manual placement coordinate | Pending |
| `right`, `left`, `above`, `below` | Preferred | Typed nodes | Relative placement helpers | Pending |
| `scope` | Preferred | Nodes accepted by scope helpers | Add node to a named scope fit group | Pending |
| `order` | Preferred | Auto-laid-out nodes | Preferred auto-layout order | Pending |
| `lane` | Preferred | Typed auto layout | Lane hint from `\lane{...}{...}` | Pending |
| `text width` | Preferred | Typed nodes | Override text wrapping width | Pending |

### Semantic Node Annotations

| Key | Status | Applies to | Purpose | Review |
| --- | --- | --- | --- | --- |
| `risk ref` | Preferred | `\risk`, `\unwantedincident` | External reference tag such as `R4` | Pending |
| `risk level` | Preferred | `\risk` | Risk-level line such as `unacceptable` | Pending |
| `likelihood` | Preferred | `\threatscenario`, `\unwantedincident` | English likelihood label such as `possible` | Pending |
| `likelihood basis` | Preferred | `\threatscenario`, `\unwantedincident` | Quantitative or ranged basis rendered in brackets | Pending |

### Common Edge Keys

| Key | Status | Applies to | Purpose | Review |
| --- | --- | --- | --- | --- |
| `asset value` | Preferred | `\assigns` | Assignment value label | Pending |
| `vulnerability` | Preferred | `\initiates` | One or more grouped vulnerabilities | Pending |
| `conditional likelihood` | Preferred | `\leadsto` | Conditional likelihood label | Pending |
| `consequence` | Preferred | `\impacts` | Consequence label | Pending |
| `treatment category` | Preferred | `\treats` | Treatment category label | Pending |
| `pos` | Preferred | Edge commands | Label position override | Pending |
| `route`, `path`, `tikz`, `label options` | Preferred | Edge commands | Drawing and styling overrides | Pending |

### Environment and Scope Options

| Key | Status | Applies to | Purpose | Review |
| --- | --- | --- | --- | --- |
| `x`, `y` | Preferred | Diagram environments | TikZ scaling | Pending |
| `layout` | Preferred | Diagram environments | `auto` or `manual` layout mode | Pending |
| `min edge gap` | Preferred | Diagram environments and nodes | Minimum enforced node-to-node spacing | Pending |
| `asset columns` | Preferred | `corasassetdiagram` | Number of auto-layout asset columns | Pending |
| `mode` | Preferred | `corastreatmentdiagram` | `overview` enables treatment-overview behavior | Pending |
| `party` | Advanced | `\corasscope` | Party node used in asset-scope corner compartment | Pending |
| `party corner` | Advanced | `\corasscope` | Corner used for the party compartment | Pending |
| `party xsep`, `party ysep`, `party tikz` | Advanced | `\corasscope` | Party-compartment spacing and styling | Pending |

## Overlap Clusters for Later Review

- Asset actor naming: `\party` is preferred; no older public actor command survives.
- Asset subtype naming: `\asset(direct|indirect)` is preferred; `\asset[...]` and `\indirectasset[...]` remain only as compatibility aliases.
- Threat/risk/treatment node naming: `\threatscenario`, `\unwantedincident`, and `\treatmentscenario` are preferred; the shorter names remain only as compatibility aliases.
- Edge semantics: `\assigns`, `\harms`, `\initiates`, `\leadsto`, `\impacts`, and `\treats` are preferred; `\cause`, `\impact`, `\relate`, `\concern`, and `\treat` are compatibility aliases.
- Structural helpers: `\junction`, `\corasscope`, `\corascontainer`, `\corasriskref`, `\corasnode`, `\corasedge`, and `\associate` remain public but should not define the first-line mental model of the package.
