#!/usr/bin/env python3
"""Unattended prototype runner without package installation."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from euroopencharts.cli import main

raise SystemExit(main(["run-example", "--data-root", "data/example", "--workers", "4"]))
