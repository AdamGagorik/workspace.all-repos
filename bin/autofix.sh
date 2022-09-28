#!/usr/bin/env bash
set -e
# shellcheck source=/dev/null
source ~/.local/pipx/venvs/all-repos/bin/activate
python -m autofix "$@"
