"""
Just prints the environment
"""

# pylint: disable=invalid-name,R0801,R0201


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
