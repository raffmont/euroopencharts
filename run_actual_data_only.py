from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from euroopencharts.actual_pipeline import run_actual_data_render

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run EuroOpenCharts actual-data-only pipeline')
    parser.add_argument('--config', default='config.json', help='Single JSON configuration file')
    args = parser.parse_args()
    result = run_actual_data_render(config_path=args.config)
    for task, paths in result.items():
        print(task)
        for p in paths:
            print(' ', p)
