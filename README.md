# SydneyTransitBench

A local Streamlit research dashboard for multimodal Sydney transport integration, quality validation, prediction and storage benchmarking. No Azure credentials or API keys are required. Seven workspaces share a version registry and provenance-preserving file adapters.

The current homepage defaults to V4 real-data mode with queried aggregates and coverage. Navigation groups the research content under Dashboard, Explore and Research. See [V4_HANDOFF.md](V4_HANDOFF.md) for source fingerprints, query verification, limitations and pending release/model inputs. The public deployment does not bundle the full raw V4 dataset; its explorer is disabled when that source is absent.

## Windows / VS Code setup

Install Python 3.11+ from python.org, open this directory in VS Code, then use its terminal:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell activation is restricted, use `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py`. Run commands from this project directory. Streamlit prints the local browser URL (normally http://localhost:8501).

Bundled example files are ready to use. `python scripts/generate_inputs.py` regenerates them, **overwriting supplied results files**, so use it only in a fresh example checkout. `python -m pytest -q` runs the core tests.

## Workspaces

Executive Overview; Data Quality and Validation; Transport Network Explorer; Arrival Delay Prediction; Occupancy Prediction; Storage and Query Performance; About the Research. Navigation, version and data mode are in the sidebar. Charts support hover, zoom and Plotly export. Tables support text search and CSV export.

Research cards use supplied metadata, never demonstration chart totals. V1 is frozen, V3 provisional, V4 awaiting validation. Frozen is not a claim of validation. October's year was not supplied and is deliberately not invented. Unknown scope dates remain empty. V3 checks overlap; their counts must not be summed. V1 model results are only visible under V1.

## Configuration and input contracts

See [INTEGRATION.md](INTEGRATION.md) for file locations, all schemas and the real-data checklist. `config/settings.json` controls default mode/version and contributor placeholders. `STB_MODE=real` overrides the mode default. A user can change mode in the sidebar. JSON was chosen instead of YAML to avoid an extra dependency.

`services/data_loader.py` owns adapters, `services/duckdb_queries.py` owns bounded Parquet access, `components/ui.py` owns chart style and table interactions. `app.py` contains seven render branches and shared navigation. New versions can be added to `config/datasets.json`; the UI reads the registry rather than requiring new pages.

## Performance and limits

The integrated dataset is never read wholesale into Pandas. DuckDB selects recognized fields, binds predicates and enforces a 2,000-row maximum. Cached previews expire after 120 seconds and include file modification time. Route/stop inputs accept exact identifiers rather than loading millions of distinct options. Add date and route filters to reduce scans. Previews are unordered, not statistically representative samples. Use compact precomputed aggregates for charts. Metrics files should be small; prediction plot inputs should be pre-sampled to at most 10,000 rows before delivery. They are local trusted research artifacts, not an arbitrary-file hosting service.

Stop maps use only supplied GTFS coordinates. Route geometry is not inferred. Model pages are evaluation viewers; they do not train models or invent prediction arrays. Benchmark charts display precomputed results and do not execute experiments. Synthetic examples are deterministic and visibly labelled.

## Research limitations

Validation decisions require the research team. The application cannot certify input provenance, statistical validity, split methodology or absence of leakage. Add split/test-period details to result provenance. Do not use actual arrival or observed passenger measurements as predictors. Delay is regression; occupancy is a 22-band multiclass task. Names and acknowledgement text must be configured by the team.
