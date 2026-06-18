from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
from concurrent.futures import ThreadPoolExecutor
from .model import TYRRHENIAN_EAST, ensure_dir
from .sources import synthetic_copernicus_bathymetry, synthetic_openseamap_seamarks
from .process import derive_contours_and_qc, derive_anchorages, make_stac
from .export import export_signalk, export_opencpn_layers, export_svg_figure, export_chart_rendering, make_manifest, zip_bundle

TaskFn = Callable[[Path], list[Path] | Path]

@dataclass
class Task:
    name: str
    fn: TaskFn
    deps: list[str] = field(default_factory=list)


class MiniDAGonStarExecutor:
    """Small local DAG executor mirroring DAGonStar task semantics for the prototype."""

    def __init__(self, root: Path, workers: int = 2):
        self.root = ensure_dir(root)
        self.workers = max(1, workers)
        self.done: dict[str, list[Path]] = {}

    def run(self, tasks: list[Task]) -> dict[str, list[Path]]:
        pending = {t.name: t for t in tasks}
        while pending:
            ready = [t for t in pending.values() if all(d in self.done for d in t.deps)]
            if not ready:
                raise RuntimeError(f"Cyclic or missing dependencies: {list(pending)}")
            with ThreadPoolExecutor(max_workers=min(self.workers, len(ready))) as ex:
                futures = {ex.submit(t.fn, self.root): t for t in ready}
                for fut, task in futures.items():
                    result = fut.result()
                    paths = result if isinstance(result, list) else [result]
                    self.done[task.name] = [Path(p) for p in paths]
                    del pending[task.name]
        return self.done


def default_tasks() -> list[Task]:
    area = TYRRHENIAN_EAST
    return [
        Task("fetch_copernicus", lambda root: synthetic_copernicus_bathymetry(area, root)),
        Task("fetch_openseamap", lambda root: synthetic_openseamap_seamarks(area, root)),
        Task("derive_bathymetry", derive_contours_and_qc, deps=["fetch_copernicus"]),
        Task("derive_anchorages", derive_anchorages, deps=["fetch_openseamap"]),
        Task("metadata_stac", lambda root: make_stac(area, root), deps=["derive_bathymetry", "derive_anchorages"]),
        Task("export_signalk", export_signalk, deps=["fetch_openseamap"]),
        Task("export_opencpn", export_opencpn_layers, deps=["derive_bathymetry", "derive_anchorages"]),
        Task("export_figure", export_svg_figure, deps=["fetch_copernicus", "fetch_openseamap"]),
        Task("export_chart_rendering", export_chart_rendering, deps=["fetch_copernicus", "fetch_openseamap", "derive_bathymetry", "derive_anchorages"]),
        Task("manifest", make_manifest, deps=["metadata_stac", "export_signalk", "export_opencpn", "export_figure", "export_chart_rendering"]),
        Task("zip_bundle", zip_bundle, deps=["manifest"]),
    ]


def run_example(root: Path, workers: int = 4) -> dict[str, list[Path]]:
    return MiniDAGonStarExecutor(root=root, workers=workers).run(default_tasks())
