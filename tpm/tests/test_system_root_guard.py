import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tpm.database import DatabaseError, validate_root


class SystemRootGuardTests(unittest.TestCase):
    def test_live_root_is_rejected_without_launcher_opt_in(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(DatabaseError):
                validate_root(Path("/"))

    def test_unmarked_directory_is_not_a_sandbox(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(DatabaseError):
                validate_root(Path(temporary))


if __name__ == "__main__":
    unittest.main()
