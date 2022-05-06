set -e
cd $( dirname ${BASH_SOURCE[0]})
# if file exists
if [ -f "./activate.sh" ]; then
  source ./activate.sh
fi

uvicorn vids_db.app:app --no-use-colors --reload --port 80 --host 0.0.0.0
