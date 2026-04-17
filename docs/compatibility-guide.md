# Compatibility Guide

The semantic-first layer is the preferred public API. Only a small set of compatibility aliases remains intentionally supported.

Retained aliases:

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

Use the [Migration Guide](semantic-api-migration.md) for one-to-one rewrites and the `\cause` dispatcher rule.
