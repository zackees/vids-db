#!/usr/bin/sh
set -e
cd $( dirname ${BASH_SOURCE[0]})
python -m webbrowser -t "http://127.0.0.1:80"
uvicorn postgress_test.app:app --no-use-colors --reload --port 80 --host 0.0.0.0
