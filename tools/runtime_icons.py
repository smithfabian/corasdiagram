#!/usr/bin/env python3
"""Shared runtime icon naming helpers for corasdiagram tooling.

The LaTeX package resolves generated runtime icon PDFs from the `icons/`
directory next to `corasdiagram.sty`, using the package-prefixed
`corasdiagram-<stem>.pdf` convention. Keep the Python build and release
helpers aligned with that naming here; the CTAN bundle layout places those
generated files under `tex/icons/`.
"""

from __future__ import annotations

from pathlib import Path


RUNTIME_ICON_PREFIX = "corasdiagram-"


def runtime_pdf_filename(stem: str) -> str:
    return f"{RUNTIME_ICON_PREFIX}{stem}.pdf"


def runtime_pdf_path(dest: Path, stem: str) -> Path:
    return dest / runtime_pdf_filename(stem)


def managed_runtime_pdf_names(source_stems: set[str]) -> set[str]:
    """Return the managed runtime PDF basenames for known icon stems.

    The returned set includes both the current prefixed runtime filenames and
    the historical unprefixed names so cleanup code can remove stale legacy
    PDFs when regenerating the managed icon set.
    """

    names = {runtime_pdf_filename(stem) for stem in source_stems}
    names.update(f"{stem}.pdf" for stem in source_stems)
    return names
