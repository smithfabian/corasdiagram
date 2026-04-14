# Changelog

All notable changes to `corasdiagram` will be documented in this file.

## [Unreleased]

- Reorganized the documentation into a clearer split between the repo landing
  page, the MkDocs user site, the printable manual, and internal maintainer
  docs.
- Replaced the old custom website stack with a Material for MkDocs
  documentation site and removed the website-only example bundle.
- Added canonical standalone examples for every diagram family plus both
  high-level table families, including a new high-level risk table example.
- Reworked the manual so it now shows complete compileable examples and rendered
  output for all diagram and table families.
- Kept `ROADMAP.md` internal only by excluding it from the public docs flow and
  release bundle.
- Stabilized the semantic-first CORAS DSL as the release target and documented
  the preferred semantic surface separately from the retained compatibility and
  advanced structural layers.
- Added a first-class migration guide with before/after rewrites for asset,
  threat, risk, and treatment diagrams, including the `\cause` dispatcher
  rules.
- Curated the regression boundary for the refactor with canonical,
  compatibility, and removal/negative fixtures, plus a local release-gate
  script for release-quality validation.
- Tightened the failure coverage for removed commands and keys so the negative
  suite now checks replacement guidance for the stabilized compatibility
  boundary.

## [0.1.2] - 2026-03-28

- Aligned the LaTeX package header date with the shipped 0.1.2 release
  metadata.
- Made the release guard validate the package `\ProvidesPackage` date against
  the matching `CHANGELOG.md` release date so future tagged releases cannot
  ship inconsistent TeX metadata.

## [0.1.1] - 2026-03-28

- Imported the upstream CORAS icon set, added `\\corasindirectasset`, and
  introduced `perspective=before|before-after|after` variants for icon-backed
  nodes and mounted-icon body nodes.
- Added the local browser-based anchor editor and improved automatic edge
  attachment for icon-backed nodes.
- Improved the high-level analysis table rendering, including scalable header
  icons and corrected threat icon overlays.
- Reworked the CTAN release bundle with a flattened `doc/` and `tex/`
  structure, top-level `NOTICE`, prefixed runtime icon filenames, relocated
  `assets/icons-src/`, and compiled example PDFs.
- Expanded the manual, project site, contribution docs, and CTAN upload tooling
  for Overleaf usage, release validation, and future automated uploads.

## [0.1.0] - 2026-03-08

- Initial public package release target.
- Added the semantic CORAS diagram package under
  `tex/latex/corasdiagram/`.
- Added package icons, canonical examples, and semantic regression tests.
- Added project metadata, contribution guidelines, release tooling, and CI
  workflows for a public repository.
