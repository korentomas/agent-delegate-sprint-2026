import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fixture_setup import prepare_pair, validate_pair
from native_run import configure_runtime, build_task
from setting import call_delegate
from inspect_ai.tool import ToolDef


class NativeTests(unittest.TestCase):
    def test_paired_payload_only_differs_by_flag_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = prepare_pair(Path(d) / "pair")
            self.assertTrue(validate_pair(p)["passed"])
            manifest = json.loads((p / "broken" / "private.json").read_text())
            self.assertNotIn(manifest["expected_flag"].encode(), (p / "broken" / "payload.tar").read_bytes())

    def test_delegate_is_a_native_serial_tool(self):
        definition = ToolDef(call_delegate())
        self.assertFalse(definition.parallel)
        self.assertEqual(definition.name, "call_delegate")
        self.assertEqual(set(definition.parameters.required), {"reason", "evidence", "attempts", "requested_help"})


if __name__ == "__main__":
    unittest.main()
