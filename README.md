# vid_db

Server for storing video information.

## Platform Unit Tests
[![Actions Status](https://github.com/zackees/vid_db/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/vid_db/actions/workflows/test_macos.yml)
[![Actions Status](https://github.com/zackees/vid_db/workflows/Win_Tests/badge.svg)](https://github.com/zackees/vid_db/actions/workflows/test_win.yml)
[![Actions Status](https://github.com/zackees/vid_db/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/vid_db/actions/workflows/test_ubuntu.yml)

# Demo

  * `pip install vid_db`
  * `vid_db --port 1234`
  * Now open up `http://127.0.0.1:1234` in a browser.

# Demo from github

  * `git clone https://github.com/zackees/vid_db`
  * `cd vid_db`
  * `pip install -e .`
  * `run_dev.sh` (Browser will open up automatically)

# Docker Production test

  * `git clone https://github.com/zackees/vid_db`
  * `cd vid_db`
  * `docker-compose up`
  * Now open up `http://127.0.0.1:80/`

# Full Tests + linting

  * `git clone https://github.com/zackees/vid_db`
  * `cd vid_db`
  * `tox`

# TODO:

  * Whoosh full search text search engine:
    * https://github.com/npcole/whoosh/tree/main/tests
