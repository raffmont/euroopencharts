from __future__ import annotations

import argparse
from pathlib import Path
from .actual_pipeline import run_actual_data_render


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='EuroOpenCharts actual-data-only research prototype')
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('run-example', help='Generate the unattended Tyrrhenian east actual-data-only bundle')
    p.add_argument('--data-root', default='data/example', help='Root for generated data products')
    p.add_argument('--workers', type=int, default=4, help='Parallel worker count')
    p2 = sub.add_parser('run-actual-data', help='Generate actual-data-only outputs with no synthetic fallback')
    p2.add_argument('--data-root', default='data/actual_data_only', help='Root for generated data products')
    p2.add_argument('--workers', type=int, default=4, help='Parallel worker count')
    args = parser.parse_args(argv)
    if args.cmd in {'run-example', 'run-actual-data'}:
        result = run_actual_data_render(Path(args.data_root), workers=args.workers)
        print('EuroOpenCharts actual-data-only pipeline completed')
        for name, paths in result.items():
            print(f'- {name}: ' + ', '.join(str(p) for p in paths))
        return 0
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
