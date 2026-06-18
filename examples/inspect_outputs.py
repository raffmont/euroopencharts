from pathlib import Path
import json

root = Path("data/example")
manifest = json.loads((root / "offline_bundle" / "manifest.json").read_text())
qc = json.loads((root / "intermediate" / "qc" / "bathymetry_qc.json").read_text())
print(manifest["name"])
print("Offline first:", manifest["offline_first"])
print("Bathymetry cells:", qc["cells"])
print("Depth range:", qc["depth_min_m"], "to", qc["depth_max_m"], "m")
