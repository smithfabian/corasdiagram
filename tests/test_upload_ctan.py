import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import upload_ctan  # noqa: E402


class UploadCtanTests(unittest.TestCase):
    def test_compose_ctan_version_uses_version_and_date(self) -> None:
        self.assertEqual(
            upload_ctan.compose_ctan_version("0.1.0", "2026-03-08"),
            "0.1.0 2026-03-08",
        )

    def test_build_fields_includes_topics_and_supported_urls_only(self) -> None:
        metadata = {
            "pkg": "corasdiagram",
            "summary": "summary",
            "description": "description",
            "ctanPath": "/graphics/pgf/contrib/corasdiagram",
            "author": ["Fabian Smith"],
            "license": ["mit"],
            "topic": ["diagram", "pgf-tikz"],
            "repository": "https://github.com/smithfabian/corasdiagram",
            "bugtracker": "https://github.com/smithfabian/corasdiagram/issues",
            "announce": "https://github.com/smithfabian/corasdiagram/releases",
            "update": True,
        }

        fields = upload_ctan.build_fields(
            metadata,
            version="0.1.0 2026-03-08",
            uploader="Fabian Smith",
            email="fabian@example.com",
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
            upload_ctan.validate_unique_metadata_urls(metadata)

    def test_announce_can_exist_in_metadata_without_being_submitted(self) -> None:
        metadata = {
            "pkg": "corasdiagram",
            "summary": "summary",
            "description": "description",
            "ctanPath": "/graphics/pgf/contrib/corasdiagram",
            "author": ["Fabian Smith"],
            "license": ["mit"],
            "announce": "https://github.com/smithfabian/corasdiagram/releases",
            "update": True,
        }

        fields = upload_ctan.build_fields(
            metadata,
            version="0.1.0 2026-03-08",
            uploader="Fabian Smith",
            email="fabian@example.com",
            announcement="",
            note="",
            update_override=None,
        )

        self.assertNotIn(
            ("announce", "https://github.com/smithfabian/corasdiagram/releases"),
            fields,
        )

    def test_read_changelog_release_date_for_current_version(self) -> None:
        from tools.versioning import read_changelog_release_date

        self.assertEqual(
            read_changelog_release_date("0.1.0", REPO_ROOT),
            "2026-03-08",
        )

    def test_missing_changelog_release_date_is_rejected(self) -> None:
        from tools.versioning import read_changelog_release_date

        with self.assertRaisesRegex(RuntimeError, "dated CHANGELOG.md entry"):
            read_changelog_release_date("9.9.9", REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
