#!/usr/bin/env bash
set -e
if [ $# -eq 0 ]
  then
    echo "Expecting the name of the fixer to apply!"
    exit 1
fi
# shellcheck source=/dev/null
source ~/.local/pipx/venvs/all-repos/bin/activate
python -m autofix.fixers."$1" "${@:2}"
