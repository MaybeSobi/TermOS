import importlib.util
import io
import re
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


DASHBOARD_PATH = (
    Path(__file__).resolve().parents[1]
    / "board"
    / "termos"
    / "rootfs-overlay"
    / "opt"
    / "termos"
    / "dashboard.py"
)

spec = importlib.util.spec_from_file_location("termos_dashboard", DASHBOARD_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load dashboard module from {DASHBOARD_PATH}")
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


class DashboardFormattingTests(unittest.TestCase):
    def test_format_bytes_uses_binary_units(self):
        self.assertEqual(dashboard.format_bytes(0), "0.0 B")
        self.assertEqual(dashboard.format_bytes(1024), "1.0 KB")
        self.assertEqual(dashboard.format_bytes(1024**2), "1.0 MB")
        self.assertEqual(dashboard.format_bytes(1024**3), "1.0 GB")
        self.assertEqual(dashboard.format_bytes(1024**4), "1.0 TB")

    def test_format_bytes_handles_fractional_values(self):
        self.assertEqual(dashboard.format_bytes(1536), "1.5 KB")

    def test_bar_renders_expected_number_of_cells(self):
        rendered = ANSI_RE.sub("", dashboard.bar(50, width=20))
        self.assertEqual(rendered.count("#"), 10)
        self.assertEqual(rendered.count("-"), 10)

    def test_bar_clamps_percentages(self):
        empty = ANSI_RE.sub("", dashboard.bar(-10, width=10))
        full = ANSI_RE.sub("", dashboard.bar(150, width=10))
        self.assertEqual(empty, "-" * 10)
        self.assertEqual(full, "#" * 10)

    def test_format_uptime_returns_a_readable_value(self):
        uptime = dashboard.format_uptime()
        self.assertRegex(uptime, r"^(?:\d+d )?\d+h \d+m$")


if __name__ == "__main__":
    unittest.main()
