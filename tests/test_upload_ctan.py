from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERSIONING_PATH = REPO_ROOT / "tools" / "versioning.py"
UPLOAD_CTAN_PATH = REPO_ROOT / "tools" / "upload_ctan.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module {name!r} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class UploadCtanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._previous_versioning = sys.modules.get("versioning")
        cls._previous_upload_ctan = sys.modules.get("upload_ctan")
        cls.versioning = load_module("versioning", VERSIONING_PATH)
        cls.upload_ctan = load_module("upload_ctan", UPLOAD_CTAN_PATH)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._previous_versioning is None:
            sys.modules.pop("versioning", None)
        else:
            sys.modules["versioning"] = cls._previous_versioning
        if cls._previous_upload_ctan is None:
            sys.modules.pop("upload_ctan", None)
        else:
            sys.modules["upload_ctan"] = cls._previous_upload_ctan

    def test_compose_ctan_version_uses_version_and_date(self) -> None:
        self.assertEqual(
            self.upload_ctan.compose_ctan_version("0.1.0", "2026-03-08"),
            "0.1.0 2026-03-08",
        )

    def test_build_fields_includes_topics_and_supported_urls_only(self) -> None:
        metadata = {
            "pkg": "corasdiagram",
            "summary": "summary",
            "description": "description",
            "ctanPath": "/graphics/pgf/contrib/corasdiagram",
            "author": ["Example Author"],
            "license": ["mit"],
            "topic": ["diagram", "pgf-tikz"],
            "repository": "https://github.com/smithfabian/corasdiagram",
            "bugtracker": "https://github.com/smithfabian/corasdiagram/issues",
            "announce": "https://github.com/smithfabian/corasdiagram/releases",
            "update": True,
        }

        fields = self.upload_ctan.build_fields(
            metadata,
            version="0.1.0 2026-03-08",
            uploader="Example Uploader",
            email="uploader@example.com",
            announcement="",
            note="",
            update_override=None,
        )

        self.assertIn(("version", "0.1.0 2026-03-08"), fields)
        self.assertIn(("topic", "diagram"), fields)
        self.assertIn(("topic", "pgf-tikz"), fields)
        self.assertIn(
            ("repository", "https://github.com/smithfabian/corasdiagram"), fields
        )
        self.assertIn(
            ("bugtracker", "https://github.com/smithfabian/corasdiagram/issues"),
            fields,
        )
        self.assertNotIn(
            ("announce", "https://github.com/smithfabian/corasdiagram/releases"),
            fields,
        )

    def test_duplicate_url_reuse_is_rejected(self) -> None:
        metadata = {
            "pkg": "corasdiagram",
            "summary": "summary",
            "description": "description",
            "ctanPath": "/graphics/pgf/contrib/corasdiagram",
            "repository": "https://github.com/smithfabian/corasdiagram",
            "development": "https://github.com/smithfabian/corasdiagram/",
        }

        with self.assertRaisesRegex(RuntimeError, "reused"):
            self.upload_ctan.validate_unique_metadata_urls(metadata)

    def test_present_non_string_url_value_is_rejected(self) -> None:
        metadata = {
            "pkg": "corasdiagram",
            "summary": "summary",
            "description": "description",
            "ctanPath": "/graphics/pgf/contrib/corasdiagram",
            "repository": ["https://github.com/smithfabian/corasdiagram"],
        }

        with self.assertRaisesRegex(TypeError, "must be a string URL"):
            self.upload_ctan.validate_unique_metadata_urls(metadata)

    def test_announce_can_exist_in_metadata_without_being_submitted(self) -> None:
        metadata = {
            "pkg": "corasdiagram",
            "summary": "summary",
            "description": "description",
            "ctanPath": "/graphics/pgf/contrib/corasdiagram",
            "author": ["Example Author"],
            "license": ["mit"],
            "announce": "https://github.com/smithfabian/corasdiagram/releases",
            "update": True,
        }

        fields = self.upload_ctan.build_fields(
            metadata,
            version="0.1.0 2026-03-08",
            uploader="Example Uploader",
            email="uploader@example.com",
            announcement="",
            note="",
            update_override=None,
        )

        self.assertNotIn(
            ("announce", "https://github.com/smithfabian/corasdiagram/releases"),
            fields,
        )

    def test_read_changelog_release_date_for_current_version(self) -> None:
        version = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        release_date = self.versioning.read_changelog_release_date(version, REPO_ROOT)
        self.assertRegex(release_date, r"^\d{4}-\d{2}-\d{2}$")

    def test_read_package_header_date_for_current_package(self) -> None:
        package_date = self.versioning.read_package_header_date(REPO_ROOT)
        self.assertRegex(package_date, r"^\d{4}/\d{2}/\d{2}$")

    def test_iso_date_to_tex_date_converts_changelog_format(self) -> None:
        self.assertEqual(
            self.versioning.iso_date_to_tex_date("2026-03-28"),
            "2026/03/28",
        )

    def test_read_changelog_release_date_allows_trailing_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "CHANGELOG.md").write_text(
                "# Changelog\r\n\r\n## [0.2.0] - 2026-03-28   \r\n\r\n- Notes.\r\n",
                encoding="utf-8",
            )

            self.assertEqual(
                self.versioning.read_changelog_release_date("0.2.0", temp_root),
                "2026-03-28",
            )

    def test_missing_changelog_release_date_is_rejected(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "dated CHANGELOG.md entry"):
            self.versioning.read_changelog_release_date("9.9.9", REPO_ROOT)

    def test_format_messages_reports_empty_response_body(self) -> None:
        self.assertEqual(
            self.upload_ctan.format_messages(""),
            "(empty response body)",
        )

    def test_format_messages_reports_empty_message_list(self) -> None:
        self.assertEqual(
            self.upload_ctan.format_messages([]),
            "(no messages returned)",
        )


if __name__ == "__main__":
    unittest.main()
