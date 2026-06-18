from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
from typing import Any


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class EOCConfig:
    path: Path
    data: dict[str, Any]

    @property
    def data_root(self) -> Path:
        root = Path(self.data.get("data_root", "data/actual_data_only"))
        if not root.is_absolute():
            root = self.path.parent / root
        return root

    @property
    def area(self) -> dict[str, Any]:
        return self.data["area"]

    def layer(self, name: str) -> dict[str, Any]:
        return self.data.get("layers", {}).get(name, {})

    def source(self, source_id: str) -> dict[str, Any]:
        return self.data.get("sources", {}).get(source_id, {})

    def relpath(self, value: str | None) -> Path | None:
        if not value:
            return None
        p = Path(value)
        if not p.is_absolute():
            p = self.path.parent / p
        return p


def load_config(config_path: str | Path | None = None) -> EOCConfig:
    selected = config_path or os.environ.get("EUROOPENCHARTS_CONFIG") or "config.json"
    path = Path(selected).expanduser().resolve()
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON configuration: {path}: {exc}") from exc
    _validate_minimal(data, path)
    return EOCConfig(path=path, data=data)


def _validate_minimal(data: dict[str, Any], path: Path) -> None:
    for key in ["project", "data_root", "area", "layers", "sources", "rendering"]:
        if key not in data:
            raise ConfigError(f"Missing required configuration key '{key}' in {path}")
    area = data["area"]
    for key in ["west", "south", "east", "north", "crs"]:
        if key not in area:
            raise ConfigError(f"Missing area.{key} in {path}")
    if data["project"].get("actual_data_only") is not True:
        raise ConfigError("project.actual_data_only must be true for production/actual-data runs")
    _validate_symbol_libraries(data, path)


def _validate_symbol_libraries(data: dict[str, Any], path: Path) -> None:
    symbols = data.get("symbols", {})
    if not symbols:
        return
    libraries = symbols.get("libraries", {})
    dictionary = symbols.get("dictionary", {})
    if not isinstance(libraries, dict) or not isinstance(dictionary, dict):
        raise ConfigError("symbols.libraries and symbols.dictionary must be objects")
    if "openbridge_icons" in libraries:
        lib = libraries["openbridge_icons"]
        if lib.get("type") != "svg":
            raise ConfigError("OpenBridge icon library must use SVG/vector assets")
        for key in ["name", "source_url", "license", "local_root"]:
            if not lib.get(key):
                raise ConfigError(f"OpenBridge icon library missing '{key}'")
    openbridge_classes = [
        name for name, entry in dictionary.items()
        if isinstance(entry, dict) and entry.get("library") == "openbridge_icons"
    ]
    for name in openbridge_classes:
        entry = dictionary[name]
        if not entry.get("asset") or not str(entry["asset"]).endswith(".svg"):
            raise ConfigError(f"OpenBridge symbol '{name}' must reference a local SVG asset")
        if "fallback_allowed" in entry and entry["fallback_allowed"] is not False:
            raise ConfigError(f"OpenBridge symbol '{name}' must not allow silent fallback")
