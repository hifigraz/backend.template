#!/usr/bin/env sh

cd $(dirname $0)

. ./venv/bin/activate

reload="Y"

clear
echo "--- formatting ---"
isor $(ls -d */ | grep -v build | grep -v venv | grep -v .egg-info)
black $(ls -d */ | grep -v build | grep -v venv | grep -v .egg-info)
echo "--- pytest ---"
pytest
echo "--- basedpyright ---"
basedpyright $(ls -d */ | grep -v build | grep -v venv | grep -v .egg-info)
echo "--- codespell ---"
codespell $(ls -d */ | grep -v build | grep -v venv | grep -v .egg-info)
echo "--- done ---"
inotifywait -t 0 --r . -e modify -e create -e delete -e move -e move_self &
kill_pid=$!
trap "kill ${kill_pid}" EXIT
wait ${kill_pid}
sleep 1

if [ "${reload}" = "Y" ]; then
  $0 $*
fi
