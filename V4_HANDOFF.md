# Week 9 V4 integration evidence

Source: `multimodal_historical_unified_V4.parquet`. The source fingerprint, full SQL aggregate output, mode coverage and four independent explorer/reference comparisons are recorded in `data/results/v4_query_evidence.json`. The source has 16,928,290 records. Aggregate generation does not approve the release; metadata stays awaiting validation until explicit team approval is supplied.

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

The homepage explains integration → eligibility/quality controls → versioned modelling table → leakage-safe held-out evaluation. Reviewer 1's exact comment and team-approved response wording have not yet been supplied, so the current rationale is not represented as an agreed reviewer response.

Pending team inputs: release approval/status; experiment result files and evaluation details; Reviewer 1's exact wording; approved hosted raw-data access. No new interface features are included in this update.
