#!/usr/bin/env sh
set -eu
PYTHONPATH=src python -m euroopencharts.cli run-example --data-root data/example --workers 4
