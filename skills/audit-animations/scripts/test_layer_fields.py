#!/usr/bin/env python3
"""Tests for the Framer layer locator fields (`layer`, `text`, `y`) added to the raw line format.

The one thing that must not break: raw files collected before these fields existed still parse,
with the three values coming back as None rather than raising or shifting other fields.

Run: python3 -m unittest discover -s <skill>/scripts -p 'test_*.py'
"""
import os, sys, tempfile, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_report
import check_page
import check_runtime
import check_safari
from common import FIELD_ESCAPE, escape_field, unescape_field, parse_int_field

# "›" is the layer-path separator; "¦" is how the collector escapes a literal "|" inside a
# field (a layer name or a text fragment may contain one).
NEW = """page=https://x.test/|slug=home|dpr=2|vw=1440|vh=900|reducedMotion=0
X|div.framer-abc>span|Hero › Title|Hola¦mundo|1024
A|div.framer-abc>span|left,transform|replace|1|0|running|Hero › Title|Hola¦mundo|1024
R|div.r|top|Footer › CTA|Escríbenos|3200
L|div.l|will-change|Nav › Logo|-|0
F|div.f|filter|blur(20px)|Card › Media|Proyecto|880
P|div.p|sticky|Nav|-|0
S|scroll|2
"""

# Exactly the format the collector emitted before layer/text/y existed.
OLD = """page=https://x.test/|slug=home|dpr=2|vw=1440|vh=900|reducedMotion=0
A|div.framer-abc>span|left,transform|replace|1|0|running
R|div.r|top
L|div.l|will-change
F|div.f|filter|blur(20px)
P|div.p|sticky
S|scroll|2
"""


def write(text):
    fh = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    fh.write(text)
    fh.close()
    return fh.name


class TestFieldEncoding(unittest.TestCase):
    def test_escape_roundtrip_of_a_pipe_in_a_layer_name(self):
        self.assertEqual(escape_field("A|B"), "A" + FIELD_ESCAPE + "B")
        self.assertEqual(unescape_field(escape_field("A|B")), "A|B")

    def test_newlines_never_survive_into_a_field(self):
        self.assertNotIn("\n", escape_field("two\nlines"))

    def test_empty_field_marker_reads_back_as_none(self):
        self.assertIsNone(unescape_field("-"))
        self.assertIsNone(unescape_field(""))
        self.assertIsNone(parse_int_field("-"))
        self.assertEqual(parse_int_field("1024"), 1024)


class TestParseNewFormat(unittest.TestCase):
    def setUp(self):
        self.path = write(NEW)
        _, self.data, self.scroll = check_page.parse_raw(self.path)

    def tearDown(self):
        os.unlink(self.path)

    def test_every_selector_line_carries_the_locator(self):
        self.assertEqual(self.data["A"][0]["layer"], "Hero › Title")
        self.assertEqual(self.data["A"][0]["text"], "Hola|mundo")  # escape decoded
        self.assertEqual(self.data["A"][0]["y"], 1024)
        self.assertEqual(self.data["R"][0]["layer"], "Footer › CTA")
        self.assertEqual(self.data["L"][0]["layer"], "Nav › Logo")
        self.assertIsNone(self.data["L"][0]["text"])          # "-" -> None
        self.assertEqual(self.data["F"][0]["layer"], "Card › Media")
        self.assertEqual(self.data["P"][0]["layer"], "Nav")

    def test_preexisting_fields_are_untouched(self):
        self.assertEqual(self.data["A"][0]["props"], ["left", "transform"])
        self.assertEqual(self.data["A"][0]["composite"], "replace")
        self.assertEqual(self.data["A"][0]["play_state"], "running")
        self.assertEqual(self.data["F"][0]["value"], "blur(20px)")
        self.assertEqual(self.data["P"][0]["position"], "sticky")
        self.assertEqual(self.scroll, 2)

    def test_x_lines_map_a_selector_to_its_locator(self):
        self.assertEqual(self.data["X"]["div.framer-abc>span"],
                         {"layer": "Hero › Title", "text": "Hola|mundo", "y": 1024})

    def test_findings_carry_the_locator(self):
        f = [f for f in check_page.check(self.data, self.scroll, "home")
             if f["source"] == "unsupported_property"][0]
        self.assertEqual(f["layer"], "Hero › Title")
        self.assertEqual(f["y"], 1024)
        s = [f for f in check_safari.check(self.data, "home")
             if f["source"] == "blur_radius_large"][0]
        self.assertEqual(s["layer"], "Card › Media")

    def test_page_level_findings_have_no_locator(self):
        f = [f for f in check_page.check(self.data, self.scroll, "home")
             if f["where"] in ("whole page", "site-wide")]
        self.assertTrue(f)
        for x in f:
            self.assertIsNone(x["layer"])
            self.assertIsNone(x["y"])


class TestParseOldFormat(unittest.TestCase):
    """A raw file collected before this change must still parse, with nulls for the new fields."""

    def setUp(self):
        self.path = write(OLD)
        _, self.data, self.scroll = check_page.parse_raw(self.path)

    def tearDown(self):
        os.unlink(self.path)

    def test_locator_fields_are_none_not_missing(self):
        for tag in ("A", "R", "L", "F", "P"):
            row = self.data[tag][0]
            self.assertIsNone(row["layer"], tag)
            self.assertIsNone(row["text"], tag)
            self.assertIsNone(row["y"], tag)

    def test_old_file_still_produces_the_same_findings(self):
        self.assertEqual(self.data["A"][0]["props"], ["left", "transform"])
        self.assertEqual(self.data["X"], {})
        sources = {f["source"] for f in check_page.check(self.data, self.scroll, "home")}
        self.assertIn("unsupported_property", sources)
        self.assertIn("will_change_static", sources)

    def test_findings_from_an_old_file_have_null_locators(self):
        f = [f for f in check_page.check(self.data, self.scroll, "home")
             if f["source"] == "unsupported_property"][0]
        self.assertIsNone(f["layer"])
        self.assertIsNone(f["text"])
        self.assertIsNone(f["y"])


class TestRuntimeEnrichment(unittest.TestCase):
    def test_apply_layers_fills_only_matching_selectors(self):
        path = write(NEW)
        try:
            layers = check_runtime.load_layers(path)
        finally:
            os.unlink(path)
        findings = [
            {"where": "div.framer-abc>span", "layer": None, "text": None, "y": None},
            {"where": "whole page", "layer": None, "text": None, "y": None},
        ]
        self.assertEqual(check_runtime.apply_layers(findings, layers), 1)
        self.assertEqual(findings[0]["layer"], "Hero › Title")
        self.assertEqual(findings[0]["y"], 1024)
        self.assertIsNone(findings[1]["layer"])

    def test_missing_layers_file_is_not_an_error(self):
        self.assertEqual(check_runtime.load_layers("/nonexistent/raw.txt"), {})


class TestReportColumns(unittest.TestCase):
    def test_layer_leads_and_selector_is_secondary(self):
        layer, selector = build_report.where_cells(
            {"where": "div.a>span", "layer": "Hero › Title", "text": "Hola", "y": 1024})
        self.assertIn("Hero › Title", layer)
        self.assertIn('"Hola"', layer)
        self.assertIn("1024px", layer)
        self.assertEqual(selector, "`div.a>span`")

    def test_without_a_layer_the_selector_stays_in_the_first_column(self):
        layer, selector = build_report.where_cells(
            {"where": "whole page", "layer": None, "text": None, "y": None})
        self.assertEqual(layer, "whole page")
        self.assertEqual(selector, "—")


if __name__ == "__main__":
    unittest.main()
