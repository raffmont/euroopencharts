# Configuration

EuroOpenCharts uses one JSON configuration file for all scripts and modules.

Default file:

```text
config.json
```

Override mechanisms:

```bash
python run_actual_data_only.py --config path/to/config.json
EUROOPENCHARTS_CONFIG=path/to/config.json python run_actual_data_only.py
```

The configuration controls:

- data root;
- area of interest;
- CRS;
- enabled layers;
- required/optional status;
- source paths;
- provenance metadata;
- output formats;
- rendering switches;
- execution backend and workers.

No operational script should hardcode these values.
