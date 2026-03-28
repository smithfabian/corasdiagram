#!/usr/bin/env python3
"""Shared runtime icon naming helpers for corasdiagram tooling.

The LaTeX package resolves generated runtime icon PDFs under tex/icons/ using
the package-prefixed corasdiagram-<stem>.pdf convention. Keep the Python build
and release helpers aligned with that naming here.
"""

from __future__ import annotations

from pathlib import Path


RUNTIME_ICON_PREFIX = "corasdiagram-"


def runtime_pdf_filename(stem: str) -> str:
    return f"{RUNTIME_ICON_PREFIX}{stem}.pdf"


def runtime_pdf_path(dest: Path, stem: str) -> Path:
    return dest / runtime_pdf_filename(stem)


def managed_runtime_pdf_names(source_stems: set[str]) -> set[str]:
    names = {runtime_pdf_filename(stem) for stem in source_stems}
    names.update(f"{stem}.pdf" for stem in source_stems)
    return names
