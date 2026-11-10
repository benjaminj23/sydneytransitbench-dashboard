# Week 9 V4 integration evidence

Source: `multimodal_historical_unified_V4.parquet`. The source fingerprint, full SQL aggregate output, mode coverage and four independent explorer/reference comparisons are recorded in `data/results/v4_query_evidence.json`. The source has 16,928,290 records and 16 columns. The team confirms publication in Azure at `curated/historical/releases/V4/multimodal_historical_unified_V4.parquet` as Frozen V4 with independent QA complete. Storage-level immutability is not confirmed. The dashboard does not claim to have read the private Azure blob or its companion reports.

Team-reported QA: 157,513 redundant cross-source LOAM records removed, zero remaining cross-source overlaps, and 210 retained exact duplicate copies. GTFS limitations are documented in the release's `KNOWN_LIMITATIONS.md`.

## Reproduce locally

```powershell
python -m services.v4_release "<path-to-final-V4.parquet>"
$env:STB_V4_PARQUET="<path-to-final-V4.parquet>"
$env:STB_TEST_V4=$env:STB_V4_PARQUET
python -m pytest -q
streamlit run app.py
```

Regeneration writes aggregate and evidence files, not the registry: review changed counts/fingerprints before updating registry fields. `config/local_paths.json` is an optional gitignored mapping of version to local Parquet path. Do not commit local paths. The dashboard rejects a V4 raw source whose fingerprint differs from the published aggregates.

## Query semantics

- Modes map BOAM/FOAM/LOAM/ROAM to Bus/Ferry/Light rail/Rail.
- `source_trip_id`, `direction`, `occupancy_range`, `source_dataset` map to the explorer's trip, direction, occupancy and source fields.
- Unique route/stop statistics count (mode, ID) pairs. They do not prove the number of distinct physical stops across all sources.
- Overall date bounds are 2026-03-23 to 2026-10-31. Per-mode counts of observed service dates are explicit; coverage is not continuous.
- GTFS trip-ID population is a measurable proxy. These queries do not independently revalidate IDs against a GTFS feed.
- Geographic scope is not independently certified. For example, the ferry query sample includes a Stockton route identifier; do not infer that all records or stops are within metropolitan Sydney without a geographic audit.
- Some BOAM values are time-only strings. They are representation differences, not automatically errors. The explorer derives delay only for parseable full timestamp pairs and leaves other delays null. Confirm date-rollover rules before using time-only rows for modelling.

## Hosted explorer boundary

The full source Parquet is approximately 238 MB and is not committed to the public repository. Local explorer verification is not hosted-data verification. The hosted app can serve reviewed aggregates without the raw file. To enable its explorer, provide an approved source-access/deployment mechanism and the same fingerprinted Parquet in the server's configured path. It must not silently substitute demonstration rows for V4.

## Modelling results and Reviewer 1

Add only completed, dataset-scoped results in the existing delay/occupancy CSVs. Optional columns `evaluation_start`, `evaluation_end` (held-out period), `evaluated_at` (experiment date), `split_strategy`, `baseline`, and `limitations` appear in the homepage summary. Existing V1 results have no supplied evaluation dates and remain labelled accordingly. No V4 performance is inferred from them.

Reviewer 1 asked what connects pipeline construction to prediction. The homepage explains how the integrated trip-stop table, eligibility rules and common features enable modelling as a downstream evaluation of analytical usefulness. The LOAM comparison is a concrete example, limited to light-rail validation.

`data/results/v4_occupancy_validation.csv` transcribes the modelling team's summary: 14 training and 5 validation service dates; exact dates and experiment artifacts are unavailable. Earlier macro F1 of 0.1506 is context only. Independent test evaluation and authorised hosted raw-data access remain pending.
