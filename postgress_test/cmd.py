"""ytclip-server command line tool."""

import os
import sys


def main() -> None:
    """Just launch postgress_test from the command line."""
    os.system("uvicorn postgress_test.app:app --no-use-colors --port 80 --host 0.0.0.0")
    sys.exit(0)


if __name__ == "__main__":
    main()
