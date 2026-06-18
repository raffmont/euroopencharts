from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import zipfile

from .config import EOCConfig, load_config
from .mpa import process_mpa_layer


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, data: dict) -> Path:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding='utf-8')
    return path


def run_actual_data_render(root: Path | None = None, workers: int | None = None, config_path: str | Path | None = None) -> dict[str, list[Path]]:
    """Run the actual-data-only rendering pipeline.

    All runtime settings are read from a single JSON configuration file. This
    pipeline never creates synthetic nautical data. Optional missing layers are
    recorded as omitted; required missing layers raise an exception.
    """
    config = load_config(config_path)
    root = ensure_dir(root or config.data_root)
    outputs: list[Path] = []
    outputs.extend(_write_actual_provenance(root, config))
    outputs.extend(process_mpa_layer(config, root))
    outputs.extend(_render_actual_chart(root, config))
    outputs.append(_write_manifest(root, config))
    outputs.append(_zip_bundle(root))
    return {'actual_data_pipeline': outputs}


def _write_actual_provenance(root: Path, config: EOCConfig) -> list[Path]:
    try:
        import mpl_toolkits.basemap_data as basemap_data
        data_dir = Path(basemap_data.__file__).parent
    except Exception:
        data_dir = None
    area = config.area
    prov = {
        'title': 'Tyrrhenian east actual-data-only rendering provenance',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'synthetic_data_used': False,
        'generated_by': 'euroopencharts.actual_pipeline.run_actual_data_render',
        'configuration_file': str(config.path),
        'area': area,
        'sources': [config.source('local_basemap_gshhs'), config.source('local_basemap_etopo1')],
        'optional_layers': {
            'marine_protected_areas': config.layer('marine_protected_areas')
        },
        'policy': 'No fallback to synthetic data. Missing online/source layers are omitted only when optional and explicitly reported.',
        'local_basemap_data_dir': str(data_dir) if data_dir else None,
        'navigation_warning': config.data['project']['navigation_warning']
    }
    return [write_json(root / 'metadata' / 'actual_data_provenance.json', prov)]


def _render_actual_chart(root: Path, config: EOCConfig) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPolygon
    import matplotlib.patheffects as pe
    from mpl_toolkits.basemap import Basemap

    area = config.area
    west, east, south, north = float(area['west']), float(area['east']), float(area['south']), float(area['north'])
    outdir = ensure_dir(root / 'figures')
    png = outdir / 'tyrrhenian_east_actual_data_chart.png'
    pdf = outdir / 'tyrrhenian_east_actual_data_chart.pdf'

    fig = plt.figure(figsize=(16, 8.4))
    ax = fig.add_subplot(111)
    ax.set_facecolor('white')

    m = Basemap(
        projection='merc',
        llcrnrlon=west, llcrnrlat=south,
        urcrnrlon=east, urcrnrlat=north,
        resolution='i', ax=ax
    )
    m.etopo(scale=0.5, alpha=0.45, zorder=0)
    m.drawmapboundary(fill_color='white', linewidth=0)
    m.fillcontinents(color='#f3e27a', lake_color='white', zorder=4)
    m.drawcoastlines(color='black', linewidth=1.3, zorder=6)
    m.drawcountries(color='0.35', linewidth=0.5, zorder=5)

    # Render authoritative MPA polygons only when the validated layer exists.
    mpa_path = root / 'intermediate' / 'derived' / 'marine_protected_areas.geojson'
    if config.data.get('rendering', {}).get('show_mpa_layer', True) and mpa_path.exists():
        mpa = json.loads(mpa_path.read_text(encoding='utf-8'))
        for feature in mpa.get('features', []):
            for ring in _polygon_rings(feature.get('geometry')):
                projected = [m(lon, lat) for lon, lat in ring]
                ax.add_patch(MplPolygon(projected, closed=True, fill=False, edgecolor='green', linewidth=1.6, linestyle=(0, (4, 3)), zorder=11))
                props = feature.get('properties', {})
                if projected:
                    xs = [p[0] for p in projected]
                    ys = [p[1] for p in projected]
                    ax.text(sum(xs)/len(xs), sum(ys)/len(ys), props.get('name', 'MPA'), fontsize=8, color='green', ha='center', zorder=12, path_effects=[pe.withStroke(linewidth=3, foreground='white')])

    ax.text(0.02, 0.965, 'ACTUAL DATA ONLY: no synthetic nautical layers',
            transform=ax.transAxes, fontsize=12, weight='bold', zorder=20,
            path_effects=[pe.withStroke(linewidth=3, foreground='white')])
    ax.text(0.02, 0.925, config.data['project']['navigation_warning'],
            transform=ax.transAxes, fontsize=10, zorder=20,
            path_effects=[pe.withStroke(linewidth=3, foreground='white')])

    # Optional layer status note, controlled by config.
    if config.data.get('rendering', {}).get('show_missing_layer_notes', True):
        omitted = root / 'metadata' / 'marine_protected_areas_omitted.json'
        if omitted.exists():
            msg = json.loads(omitted.read_text(encoding='utf-8')).get('reason', 'MPA layer omitted')
            ax.text(0.02, 0.885, f'MPA layer omitted: {msg}', transform=ax.transAxes, fontsize=9, zorder=20,
                    path_effects=[pe.withStroke(linewidth=3, foreground='white')])

    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.savefig(png, dpi=200, bbox_inches='tight', pad_inches=0.02)
    fig.savefig(pdf, bbox_inches='tight', pad_inches=0.02)
    plt.close(fig)
    return [png, pdf]


def _polygon_rings(geometry: dict | None) -> list[list[list[float]]]:
    if not geometry:
        return []
    gtype = geometry.get('type')
    coords = geometry.get('coordinates', [])
    if gtype == 'Polygon':
        return [coords[0]] if coords else []
    if gtype == 'MultiPolygon':
        return [poly[0] for poly in coords if poly]
    return []


def _write_manifest(root: Path, config: EOCConfig) -> Path:
    files = []
    for p in sorted(root.rglob('*')):
        if p.is_file():
            files.append(str(p.relative_to(root)))
    return write_json(root / 'offline_bundle' / 'manifest.json', {
        'name': 'tyrrhenian-east-actual-data-only',
        'offline_first': True,
        'synthetic_data_used': False,
        'configuration_file': str(config.path),
        'outputs': files,
        'marine_protected_areas': {
            'enabled': bool(config.layer('marine_protected_areas').get('enabled', False)),
            'required': bool(config.layer('marine_protected_areas').get('required', False)),
            'available': (root / 'intermediate' / 'derived' / 'marine_protected_areas.geojson').exists(),
        },
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'warning': config.data['project']['navigation_warning']
    })


def _zip_bundle(root: Path) -> Path:
    out = ensure_dir(root / 'dist') / 'tyrrhenian-east-actual-data-only-bundle.zip'
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file() and 'dist' not in p.relative_to(root).parts:
                z.write(p, p.relative_to(root))
    return out
