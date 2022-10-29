"""
Just prints the environment
"""

import os
import unittest
from pprint import pprint


class PrintEnv(unittest.TestCase):
    """Just prints the environment"""

    def test_print_env(self) -> None:
        """Test the full text search database."""
        pprint(dict(os.environ))


if __name__ == "__main__":
    unittest.main()
