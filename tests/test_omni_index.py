"""Tests for shared/omni_index.py. Run: python3 -m unittest discover -s tests"""

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("omni_index", ROOT / "shared" / "omni_index.py")
oi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oi)

EXAMPLE_INDEX = ROOT / "examples" / "omni-index.md"
EXAMPLE_CONFIG = ROOT / "examples" / "omni-config.md"


def run(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = oi.main(list(argv))
    return code, buf.getvalue()


class ExampleIndexTests(unittest.TestCase):
    def test_example_index_is_valid(self):
        code, out = run("validate", str(EXAMPLE_INDEX))
        self.assertEqual(code, 0, out)

    def test_search_ranks_title_match_first(self):
        entries = oi.parse_index(EXAMPLE_INDEX.read_text())
        results = oi.search(entries, "membership pricing", {})
        self.assertTrue(results)
        self.assertEqual(results[0][1]["id"], "omni-20260520-membership-pricing-decision")

    def test_vocabulary_expands_synonyms(self):
        entries = oi.parse_index(EXAMPLE_INDEX.read_text())
        vocab = oi.parse_vocabulary(EXAMPLE_CONFIG.read_text())
        plain = oi.search(entries, "tiers", {})
        expanded = oi.search(entries, "tiers", vocab)
        self.assertGreater(len(expanded), len(plain))

    def test_superseded_ranks_below_active(self):
        entries = oi.parse_index(EXAMPLE_INDEX.read_text())
        ids = [e["id"] for _, e in oi.search(entries, "pricing", {})]
        self.assertLess(ids.index("omni-20260520-membership-pricing-decision"),
                        ids.index("omni-20260305-pricing-workshop-notes"))

    def test_filters(self):
        code, out = run("search", str(EXAMPLE_INDEX), "pricing", "--source", "slack")
        self.assertEqual(code, 0)
        self.assertIn("annual-discount", out)
        self.assertNotIn("membership-pricing-decision", out)

    def test_no_match_exit_code(self):
        code, out = run("search", str(EXAMPLE_INDEX), "zzzz-nothing")
        self.assertEqual(code, 1)
        self.assertIn("no matches", out)


class ValidationTests(unittest.TestCase):
    def check(self, block):
        entries = oi.parse_index("# Omni Index\n\n" + block)
        return oi.validate_entries(entries)

    def test_missing_fields_and_bad_values(self):
        errors = self.check(
            "## omni-20261399-bad · Bad\n- kind: rumour\n- source: nowhere\n- date: 2026-13-01\n"
        )
        text = "\n".join(errors)
        for fragment in ("impossible date", "missing 'summary'", "kind 'rumour'",
                         "source must be", "not a valid"):
            self.assertIn(fragment, text)

    def test_duplicate_id_and_location(self):
        entry = ("## omni-20260101-a · A\n- kind: doc\n- summary: s\n- topics: t\n"
                 "- source: local / x\n- location: /x.md\n- date: 2026-01-01\n\n")
        errors = self.check(entry + entry)
        self.assertTrue(any("duplicate id" in e for e in errors))
        self.assertTrue(any("same location" in e for e in errors))

    def test_summary_length(self):
        errors = self.check("## omni-20260101-a · A\n- kind: doc\n- summary: " + "x" * 401 +
                            "\n- topics: t\n- source: local / x\n- location: /x\n- date: 2026-01-01\n")
        self.assertTrue(any("max 400" in e for e in errors))


class WriteTests(unittest.TestCase):
    def test_init_add_validate_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = str(Path(tmp) / "omni-index.md")
            self.assertEqual(run("init", index, "--owner", "Test")[0], 0)
            code, out = run("add", index, "--title", "Launch plan", "--kind", "doc",
                            "--summary", "Three-step launch.", "--topics", "Launch, Plan",
                            "--source", "drive / Team", "--location", "https://x/1",
                            "--date", "2026-02-01")
            self.assertEqual(code, 0, out)
            new_id = out.strip()
            self.assertRegex(new_id, r"^omni-\d{8}-launch-plan$")
            # A second add with the same title gets a unique id; same location is rejected.
            code, out = run("add", index, "--title", "Launch plan", "--kind", "doc",
                            "--summary", "Other.", "--topics", "launch",
                            "--source", "drive / Team", "--location", "https://x/1",
                            "--date", "2026-02-02")
            self.assertEqual(code, 1)
            self.assertIn("not added", out)
            code, _ = run("add", index, "--title", "Launch plan", "--kind", "doc",
                          "--summary", "Other.", "--topics", "launch",
                          "--source", "drive / Team", "--location", "https://x/2",
                          "--date", "2026-02-02")
            self.assertEqual(code, 0)
            self.assertEqual(run("validate", index)[0], 0)
            entries = oi.parse_index(Path(index).read_text())
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0]["topics"], "launch, plan")

    def test_init_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "omni-index.md"
            index.write_text("keep me")
            with self.assertRaises(SystemExit):
                run("init", str(index))
            self.assertEqual(index.read_text(), "keep me")

    def test_stats(self):
        code, out = run("stats", str(EXAMPLE_INDEX), "--json")
        self.assertEqual(code, 0)
        self.assertIn('"by_source"', out)


if __name__ == "__main__":
    unittest.main()
