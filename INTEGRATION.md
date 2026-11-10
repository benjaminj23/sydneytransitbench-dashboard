# Integration guide and input schemas

All paths are relative to the project root unless an absolute local path is configured. No cloud setup is needed. Each registry entry may override `integrated`, `quality`, `aggregates`, `delay`, `occupancy`, `benchmarks`, `predictions`, `bands`, `confusion`, `distance` and `stops`. Otherwise adapters use `data/results/<kind>.csv` and `data/gtfs/stops.csv`. CSV headers are available in `data/templates/`; JSON alternatives are arrays of row objects and require a `.json` configured path.

## V4 handoff

1. Place V4 Parquet at `data/integrated/v4.parquet` (or configure a local path). A single Parquet file or directory of Parquet partitions is supported by DuckDB.
2. Place compact quality rows in `data/results/quality.csv`, aggregate rows in `aggregates.csv`, model results in `delay.csv` and `occupancy.csv`, benchmark repetitions in `benchmarks.csv`. Keep `dataset_version=V4`; never relabel V1 benchmarks.
3. Optional diagnostics go in `predictions.csv`, `bands.csv`, `confusion.csv`, `distance.csv`; verified GTFS stops go in `data/gtfs/stops.csv`.
4. Set V4 records, date coverage, unique routes/stops, provenance and update date in `config/datasets.json`. Leave `validated=false` and status `awaiting validation` until explicit team approval. Only after approval set `validated=true` and `status=validated`.
5. Set `mode` to `real` and `default_version` to `V4` in settings, or select them in the sidebar. Populate contributor details and approved acknowledgement text.
6. Run tests, launch the app, inspect each page and reconcile record totals to the authoritative output. Missing optional inputs should show empty states. Confirm that no illustrative charts appear in real mode.

## Common conventions

`dataset_version` is an exact registry key. `synthetic` is an explicit true/false boolean in CSV or JSON. Research adapters exclude synthetic rows even in demo mode; demo adapters reject research rows. `provenance` states source, evaluation split or scope; `updated` should be an ISO date when known. Missing values are empty cells, not zero. Use numeric fractions 0–1 for accuracy/F1/rates, minutes for delay, seconds for query runs, decimal MB for storage. Empty schema templates contain no invented results.

## Schemas

- Integrated Parquet (16-column common contract): `dataset_version, source, mode, service_date, route_id, trip_id, direction_id, stop_id, stop_sequence, scheduled_arrival, actual_arrival, arrival_delay_minutes, occupancy_band, gtfs_route_id, gtfs_stop_id, quality_flags`. IDs are strings; sequence integer; date ISO YYYY-MM-DD; arrivals timezone-consistent timestamps; delay nullable numeric; flags string. This is an application adapter contract, not a claim about your original unpublished 16-column schema: rename/map upstream fields as needed. Missing optional fields are omitted in previews; filtering an unavailable field reports an error.
- Quality: `dataset_version, mode, start_date, end_date, scope, category, metric, value, unit, status, synthetic, provenance, updated`. One row per distinct check/scope. Scope dates ISO if known, otherwise blank. Units records/groups/fraction as applicable. Categories include Missing values, Deduplication, Duplicate keys, Conflicting keys, Timestamp anomalies, GTFS, Source summary. Add source-level rows with explicit source in scope/mode. Never treat group counts as record counts.
- Aggregates: `dataset_version, mode, service_date, records, missing_scheduled, missing_actual, gtfs_matches, gtfs_eligible, synthetic, provenance, updated`. One disjoint daily mode aggregate per row. GTFS eligible is the rate denominator, not necessarily all records.
- Delay: `dataset_version, model, mae, synthetic, provenance, updated`; optional `rmse, within_5`. Lower MAE/RMSE is better. `within_5` is a fraction. Blank optional metrics stay unavailable.
- Occupancy: `dataset_version, model, accuracy, macro_f1, synthetic, provenance, updated`. Keep the original 22 ordered target bands; do not collapse to low/medium/high. Add classifiers as rows.
- Predictions: `dataset_version, model, actual_delay, predicted_delay, synthetic, provenance, updated`. Pre-sample visualisation rows upstream (maximum recommended 10,000); no prediction values are supplied with this project.
- Bands: `dataset_version, band, count, synthetic, provenance, updated`. Supply confirmed labels in intended order.
- Confusion: `dataset_version, model, actual_band, predicted_band, count, synthetic, provenance, updated`. Supply all intended cells, including zero counts; absent cells remain missing.
- Distance: `dataset_version, model, band_distance, count, synthetic, provenance, updated`. Distance is absolute difference between ordinal band indexes, not passenger counts.
- Benchmarks: `dataset_version, mode, category, format, workload, records, size_mb, seconds, repetition, hardware, software, synthetic, provenance, updated`. One measured run per row; format CSV or Parquet. Hardware/software strings must identify comparable environments; provenance should include query text, cache policy, timing boundary and experiment ID. Repeated file sizes are summarized by maximum within a comparison group. Do not mix independent experiments under identical group keys.
- Stops: `stop_id, stop_name, stop_lat, stop_lon, provenance`. Use verified GTFS coordinates only; source coordinates are not supplied in the examples.

## Real-mode review checklist

- [ ] All real files carry the correct dataset version and `synthetic=false`.
- [ ] Scope, date, status, provenance and update fields are reviewed.
- [ ] V4 validation has explicit team approval before enabling the validated flag.
- [ ] Quality categories are interpreted separately; October counts are not whole-V3 totals.
- [ ] Model splits and leakage controls are documented; no post-event predictors were used.
- [ ] Benchmark runs compare identical record scopes and environments.
- [ ] Real mode shows no demonstration inputs; unknown metrics remain empty.
- [ ] Every page and the bounded explorer have been checked on the target laptop.
