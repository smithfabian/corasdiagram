from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "coras_anchor_editor.py"


def load_module():
    spec = importlib.util.spec_from_file_location("coras_anchor_editor", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CorasAnchorEditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.package_path = cls.module.PACKAGE_PATH
        cls.package_text = cls.package_path.read_text(encoding="utf-8")

    def test_parse_package_symbols_reads_all_editable_symbols(self) -> None:
        symbols = self.module.parse_package_symbols(self.package_path)
        self.assertEqual(set(symbols), set(self.module.EDITABLE_SYMBOL_MAP))
        for symbol_data in symbols.values():
            self.assertEqual(set(symbol_data["anchors"]), set(self.module.ANCHOR_ORDER))

    def test_apply_anchor_updates_round_trips_without_changes(self) -> None:
        symbols = self.module.parse_package_symbols(self.package_path)
        updates = {
            symbol: {
                anchor: {"x": coords["x"], "y": coords["y"]}
                for anchor, coords in symbol_data["anchors"].items()
            }
            for symbol, symbol_data in symbols.items()
        }
        rewritten = self.module.apply_anchor_updates(self.package_text, updates)
        self.assertEqual(rewritten, self.package_text)

    def test_apply_anchor_updates_changes_only_requested_anchor_line(self) -> None:
        symbols = self.module.parse_package_symbols(self.package_path)
        original_north = symbols["asset"]["anchors"]["north"]
        updates = {
            "asset": {
                "north": {"x": original_north["x"] + 0.1, "y": original_north["y"]},
            }
        }
        rewritten = self.module.apply_anchor_updates(self.package_text, updates)
        original_lines = self.package_text.splitlines()
        rewritten_lines = rewritten.splitlines()
        changed_lines = [index for index, pair in enumerate(zip(original_lines, rewritten_lines)) if pair[0] != pair[1]]
        self.assertEqual(len(changed_lines), 1)
        changed_line = rewritten_lines[changed_lines[0]]
        self.assertIn(r"\corasdiagram@setsymbolanchor{asset}{north}{0.1mm}{5.75mm}%", changed_line)
        self.assertIn(
            r"\corasdiagram@setsymbolanchor{stakeholder}{north}{0mm}{5.55mm}%",
            rewritten,
        )

    def test_save_anchor_updates_writes_backup_and_valid_mm_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "corasdiagram.sty"
            temp_path.write_text(self.package_text, encoding="utf-8")
            updates = {
                "stakeholder": {
                    "east": {"x": 2.91, "y": 1.04},
                }
            }
            result = self.module.save_anchor_updates(temp_path, updates)
            saved_text = temp_path.read_text(encoding="utf-8")
            self.assertTrue((temp_path.with_suffix(".sty.bak")).exists())
            self.assertIn(r"\corasdiagram@setsymbolanchor{stakeholder}{east}{2.9mm}{1.05mm}%", saved_text)
            self.assertIn("symbols", result)

    def test_sanitize_svg_for_browser_rewrites_legacy_namespaces(self) -> None:
        raw_svg = (
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" [\n'
            '  <!ENTITY ns_svg "http://www.w3.org/2000/svg">\n'
            '  <!ENTITY ns_xlink "http://www.w3.org/1999/xlink">\n'
            ']>\n'
            '<svg xmlns="&amp;ns_svg;" xmlns:xlink="&amp;ns_xlink;" width="10" height="10"></svg>\n'
        )
        sanitized = self.module.sanitize_svg_for_browser(raw_svg)
        self.assertNotIn("<!DOCTYPE svg", sanitized)
        self.assertIn('xmlns="http://www.w3.org/2000/svg"', sanitized)
        self.assertIn('xmlns:xlink="http://www.w3.org/1999/xlink"', sanitized)


if __name__ == "__main__":
    unittest.main()
