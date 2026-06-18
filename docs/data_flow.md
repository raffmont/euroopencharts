# Data flow

```text
config.json
  -> validate configuration
  -> validate OpenBridge SVG symbol dictionary when configured
  -> acquire/validate actual sources
  -> validate source resolution and freshness metadata
  -> validate MPA geometry and rules if configured
  -> write provenance and omission reports
  -> render copyright-safe nautical chart figure
  -> build offline bundle
```

Every output is derived from actual source data or explicit omission metadata. No synthetic replacement layer is created.
