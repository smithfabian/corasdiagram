from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VERSIONING_PATH = REPO_ROOT / "tools" / "versioning.py"
RUNTIME_ICONS_PATH = REPO_ROOT / "tools" / "runtime_icons.py"
BUILD_RELEASE_PATH = REPO_ROOT / "tools" / "build_release.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BuildReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._previous_versioning = sys.modules.get("versioning")
        cls._previous_runtime_icons = sys.modules.get("runtime_icons")
        cls._previous_build_release = sys.modules.get("build_release")
        cls.versioning = load_module("versioning", VERSIONING_PATH)
        cls.runtime_icons = load_module("runtime_icons", RUNTIME_ICONS_PATH)
        cls.build_release = load_module("build_release", BUILD_RELEASE_PATH)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._previous_versioning is None:
            sys.modules.pop("versioning", None)
        else:
            sys.modules["versioning"] = cls._previous_versioning
        if cls._previous_runtime_icons is None:
            sys.modules.pop("runtime_icons", None)
        else:
            sys.modules["runtime_icons"] = cls._previous_runtime_icons
        if cls._previous_build_release is None:
            sys.modules.pop("build_release", None)
        else:
            sys.modules["build_release"] = cls._previous_build_release

    def test_tracked_example_stems_matches_canonical_examples(self) -> None:
        self.assertEqual(
            self.build_release.tracked_example_stems(REPO_ROOT),
            [
                "corasdiagram-demo",
                "corasdiagram-high-level-analysis-table",
                "corasdiagram-minimal",
                "corasdiagram-website-examples",
            ],
        )

    def test_copy_example_artifacts_requires_matching_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            source_dir = repo_root / "examples"
            dest_dir = Path(temp_dir) / "bundle"
            source_dir.mkdir()
            (source_dir / "example.tex").write_text("% source", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Missing compiled example PDF"):
                self.build_release.copy_example_artifacts(
                    repo_root, source_dir, dest_dir, ["example"]
                )

    def test_copy_example_artifacts_copies_only_canonical_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            source_dir = repo_root / "examples"
            dest_dir = Path(temp_dir) / "bundle"
            source_dir.mkdir()
            (source_dir / "example.tex").write_text("% example", encoding="utf-8")
            (source_dir / "example.pdf").write_bytes(b"%PDF-1.4\n")
            (source_dir / "stray.pdf").write_bytes(b"%PDF-1.4\n")

            self.build_release.copy_example_artifacts(
                repo_root, source_dir, dest_dir, ["example"]
            )

            self.assertTrue((dest_dir / "example.tex").exists())
            self.assertTrue((dest_dir / "example.pdf").exists())
            self.assertFalse((dest_dir / "stray.pdf").exists())

    def test_copy_example_artifacts_accepts_root_level_pdf_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            source_dir = repo_root / "examples"
            dest_dir = repo_root / "bundle"
            source_dir.mkdir()
            (source_dir / "example.tex").write_text("% example", encoding="utf-8")
            (repo_root / "example.pdf").write_bytes(b"%PDF-1.4\n")

            self.build_release.copy_example_artifacts(
                repo_root, source_dir, dest_dir, ["example"]
            )

            self.assertTrue((dest_dir / "example.tex").exists())
            self.assertTrue((dest_dir / "example.pdf").exists())

    def test_verify_example_archive_names_requires_tex_and_pdf_pairs(self) -> None:
        archive_names = {
            "corasdiagram/doc/examples/corasdiagram-demo.tex",
            "corasdiagram/doc/examples/corasdiagram-demo.pdf",
        }
        self.build_release.verify_example_archive_names(
            archive_names, ["corasdiagram-demo"]
        )

        with self.assertRaisesRegex(RuntimeError, "canonical example artifacts"):
            self.build_release.verify_example_archive_names(
                {"corasdiagram/doc/examples/corasdiagram-demo.tex"},
                ["corasdiagram-demo"],
            )


if __name__ == "__main__":
    unittest.main()
