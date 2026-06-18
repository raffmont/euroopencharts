from __future__ import annotations

import argparse
from pathlib import Path
from .actual_pipeline import run_actual_data_render
from .config import ConfigError
from .high_quality import prepare_high_quality_run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='EuroOpenCharts actual-data-only research prototype')
    sub = parser.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('run-example', help='Generate the unattended Tyrrhenian east actual-data-only bundle')
    p.add_argument('--data-root', default='data/example', help='Root for generated data products')
    p.add_argument('--workers', type=int, default=4, help='Parallel worker count')
    p2 = sub.add_parser('run-actual-data', help='Generate actual-data-only outputs with no synthetic fallback')
    p2.add_argument('--data-root', default='data/actual_data_only', help='Root for generated data products')
    p2.add_argument('--workers', type=int, default=4, help='Parallel worker count')
    p2.add_argument('--config', default=None, help='Single JSON configuration file')
    p3 = sub.add_parser('prepare-high-quality', help='Download and validate configured high-quality official sources')
    p3.add_argument('--config', default='config.json', help='Single JSON configuration file')
    p3.add_argument('--strict', action='store_true', help='Fail if any required high-quality source, MPA input, freshness check, or OpenBridge SVG asset is incomplete')
    p3.add_argument('--write-config', action='store_true', help='Replace placeholder URLs with explicit official_url values already present in the config')
    args = parser.parse_args(argv)
    if args.cmd in {'run-example', 'run-actual-data'}:
        result = run_actual_data_render(Path(args.data_root), workers=args.workers, config_path=getattr(args, 'config', None))
        print('EuroOpenCharts actual-data-only pipeline completed')
        for name, paths in result.items():
            print(f'- {name}: ' + ', '.join(str(p) for p in paths))
        return 0
    if args.cmd == 'prepare-high-quality':
        try:
            result = prepare_high_quality_run(args.config, strict=args.strict, write_config=args.write_config)
        except ConfigError as exc:
            print(f'EuroOpenCharts configuration error: {exc}')
            return 1
        print('EuroOpenCharts high-quality source preparation completed')
        print(f'- ready: {result.ready}')
        print(f'- manifest: {result.manifest}')
        for path in result.outputs:
            print(f'  {path}')
        return 0
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
