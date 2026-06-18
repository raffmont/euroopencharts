from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from euroopencharts.config import ConfigError
from euroopencharts.actual_pipeline import run_actual_data_render


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create the highest-quality actual-data-only map configured by one JSON file."
    )
    parser.add_argument(
        "--config",
        default=str(Path(__file__).with_name("highest_quality_map_config.json")),
        help="Single JSON configuration file controlling downloads, sources, rendering and outputs.",
    )
    args = parser.parse_args()
    try:
        result = run_actual_data_render(config_path=args.config)
    except ConfigError as exc:
        print(f"EuroOpenCharts configuration error: {exc}", file=sys.stderr)
        return 1
    print("EuroOpenCharts highest-quality actual-data-only map completed")
    for task, paths in result.items():
        print(task)
        for path in paths:
            print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
