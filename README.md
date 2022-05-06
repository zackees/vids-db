# vids_db

Server for storing video information.

## Platform Unit Tests
[![Actions Status](https://github.com/zackees/vids-db/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/vids-db/actions/workflows/test_macos.yml)
[![Actions Status](https://github.com/zackees/vids-db/workflows/Win_Tests/badge.svg)](https://github.com/zackees/vids-db/actions/workflows/test_win.yml)
[![Actions Status](https://github.com/zackees/vids-db/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/vids-db/actions/workflows/test_ubuntu.yml)

# Demo

  * `pip install vids-db`
  * `vids-db --port 1234`
  * Now open up `http://127.0.0.1:1234` in a browser.

# Demo from github

  * `git clone https://github.com/zackees/vids-db`
  * `cd vids_db`
  * `pip install -e .`
  * `run_dev.sh` (Browser will open up automatically)

# Docker Production test

  * `git clone https://github.com/zackees/vids-db`
  * `cd vids_db`
  * `docker-compose up`
  * Now open up `http://127.0.0.1:80/`

# Full Tests + linting

  * `git clone https://github.com/zackees/vids-db`
  * `cd vids_db`
  * `tox`

