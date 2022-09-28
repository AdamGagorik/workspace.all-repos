#!/usr/bin/env bash
set -e
source ~/.local/pipx/venvs/all-repos/bin/activate
python -m autofix $@
