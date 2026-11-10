# Verification

## V4 integration — 11 November 2026 (Sydney)

`python -m pytest -q` with `STB_TEST_V4` set to the actual Downloads source: **15 passed**. Full-source DuckDB aggregation reconciled daily totals, mode totals and 16,928,290 integrated records. Four combined explorer filter cases were compared with independent SQL reference counts; the 2,000-row cap, literal injection-like filter and time-only arrival handling were exercised. Source SHA-256 and per-case evidence are in `data/results/v4_query_evidence.json`.

These checks establish local source/query behavior. Independent release QA and the Frozen V4 designation were subsequently confirmed by the team. The LOAM validation metrics are team-reported; exact dates, experiment files and independent test results were not supplied. Hosted raw-data access remains unavailable.

## Initial application verification

Executed on 5 November 2026 using workspace-local Python 3.11.15, Streamlit 1.66.1, Pandas 2.3.3, DuckDB 1.5.6, Plotly 6.9.0 and PyArrow 23.0.1.

- `python -m pytest -q`: **11 passed**, including Streamlit AppTest render checks for all seven demo pages, real-mode V4 empty states, V1 model results and the demo explorer.
- Streamlit server launched successfully on local port 8501.
- HTTP `/_stcore/health` returned `ok`.

No browser screenshot review was performed. AppTest verifies script execution and widget behavior, not visual layout. Multimillion-row performance has not been measured because the research Parquet files were not provided. Run the real-data checklist on the presentation laptop after integration.
