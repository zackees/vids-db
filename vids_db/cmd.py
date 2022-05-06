"""vids_db command line tool."""

import os
import sys
import webbrowser


def main() -> None:
    """Just launch vids_db from the command line."""
    webbrowser.open_new_tab("http://127.0.0.1:80")
    os.system("uvicorn vids_db.app:app --no-use-colors --port 80 --host 0.0.0.0")
    sys.exit(0)


if __name__ == "__main__":
    main()
