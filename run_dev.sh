set -e
cd $( dirname ${BASH_SOURCE[0]})
# if file exists
if [ -f "./activate.sh" ]; then
  source ./activate.sh
fi

export VID_DB_FILE="data/run_dev.sqlite"
python -m webbrowser -t "http://127.0.0.1:80"
uvicorn vid_db.app:app --no-use-colors --reload --port 80 --host 0.0.0.0
