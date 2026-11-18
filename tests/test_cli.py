import unittest

from termos import __version__
from termos.cli import build_parser, system_info


class CliTests(unittest.TestCase):
    def test_version_is_development_version(self):
        self.assertTrue(__version__.startswith("0.3.0"))

    def test_parser_accepts_info(self):
        args = build_parser().parse_args(["info"])
        self.assertEqual(args.command, "info")

    def test_system_info_has_expected_fields(self):
        info = system_info()
        self.assertEqual(set(info), {"distribution", "kernel", "architecture", "python"})
        self.assertTrue(all(isinstance(value, str) for value in info.values()))


if __name__ == "__main__":
    unittest.main()
