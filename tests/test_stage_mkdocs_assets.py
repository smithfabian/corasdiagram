from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE_MKDOCS_ASSETS_PATH = REPO_ROOT / "tools" / "stage_mkdocs_assets.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module {name!r} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class StageMkDocsAssetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._previous_stage_mkdocs_assets = sys.modules.get("stage_mkdocs_assets")
        cls.stage_mkdocs_assets = load_module(
            "stage_mkdocs_assets", STAGE_MKDOCS_ASSETS_PATH
        )

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._previous_stage_mkdocs_assets is None:
            sys.modules.pop("stage_mkdocs_assets", None)
        else:
            sys.modules["stage_mkdocs_assets"] = cls._previous_stage_mkdocs_assets

    def make_repo_root(self, temp_dir: str) -> Path:
        repo_root = Path(temp_dir) / "repo"
        (repo_root / "examples").mkdir(parents=True)
        (repo_root / "docs" / "assets" / "generated").mkdir(parents=True)
        return repo_root

    def test_validate_output_dir_accepts_default_generated_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = self.make_repo_root(temp_dir)
            output_root = repo_root / "docs" / "assets" / "generated"

            resolved = self.stage_mkdocs_assets.validate_output_dir(
                repo_root, output_root
            )

            self.assertEqual(resolved, output_root.resolve())

    def test_validate_output_dir_accepts_descendant(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = self.make_repo_root(temp_dir)
            output_root = repo_root / "docs" / "assets" / "generated" / "preview"

            resolved = self.stage_mkdocs_assets.validate_output_dir(
                repo_root, output_root
            )

            self.assertEqual(resolved, output_root.resolve())

    def test_validate_output_dir_rejects_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = self.make_repo_root(temp_dir)

            with self.assertRaisesRegex(
                RuntimeError,
                "Output dir must be the generated-docs tree or one of its descendants",
            ):
                self.stage_mkdocs_assets.validate_output_dir(repo_root, repo_root)

    def test_validate_output_dir_rejects_outside_generated_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = self.make_repo_root(temp_dir)
            outside = repo_root / "docs" / "assets"

            with self.assertRaisesRegex(
                RuntimeError,
                "Output dir must be the generated-docs tree or one of its descendants",
            ):
                self.stage_mkdocs_assets.validate_output_dir(repo_root, outside)

    def test_resolve_example_pdf_uses_examples_dir_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = self.make_repo_root(temp_dir)
            (repo_root / "example.pdf").write_bytes(b"%PDF-root\n")

            with self.assertRaisesRegex(RuntimeError, "Missing compiled example PDF"):
                self.stage_mkdocs_assets.resolve_example_pdf(repo_root, "example")

    def test_stage_assets_requires_example_pdf_in_examples_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = self.make_repo_root(temp_dir)
            doc_pdf = repo_root / "manual.pdf"
            doc_pdf.write_bytes(b"%PDF-manual\n")
            (repo_root / "examples" / "example.tex").write_text(
                "% example", encoding="utf-8"
            )

            with self.assertRaisesRegex(RuntimeError, "Missing compiled example PDF"):
                self.stage_mkdocs_assets.stage_assets(
                    repo_root,
                    doc_pdf,
                    repo_root / "docs" / "assets" / "generated",
                )

    def test_stage_assets_stages_manual_and_example_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = self.make_repo_root(temp_dir)
            doc_pdf = repo_root / "manual.pdf"
            doc_pdf.write_bytes(b"%PDF-manual\n")
            (repo_root / "examples" / "example.tex").write_text(
                "% example", encoding="utf-8"
            )
            (repo_root / "examples" / "example.pdf").write_bytes(b"%PDF-example\n")

            output_root = self.stage_mkdocs_assets.stage_assets(
                repo_root,
                doc_pdf,
                repo_root / "docs" / "assets" / "generated",
            )

            self.assertEqual(
                output_root, (repo_root / "docs" / "assets" / "generated").resolve()
            )
            self.assertTrue(
                (output_root / "manual" / "corasdiagram-doc.pdf").is_file()
            )
            self.assertTrue((output_root / "examples" / "example.tex").is_file())
            self.assertTrue((output_root / "examples" / "example.pdf").is_file())


if __name__ == "__main__":
    unittest.main()
