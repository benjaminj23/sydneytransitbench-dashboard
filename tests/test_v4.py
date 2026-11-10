import hashlib
import json
import os
from pathlib import Path
import pytest
from services.data_loader import ROOT,registry,load
from services.duckdb_queries import preview

def test_v4_release_reconciliation():
    meta=registry()['V4']; rows=load('aggregates','V4','real')
    assert not rows.empty and not rows.synthetic.any()
    assert rows.records.sum()==meta['records']==sum(r['records'] for r in meta['mode_totals'])
    assert not meta['allow_demo']
    assert meta['validated'] is True and meta['status']=='frozen'

def test_v4_occupancy_metrics_are_validation_only():
    results=load('occupancy','V4','real').set_index('model')
    assert results.evaluation_stage.eq('Validation').all()
    assert results.loc['Unified historical model','macro_f1']==0.1711
    assert results.loc['Separate route models','band_mae']==0.5912
    assert results['limitations'].str.contains('independent test pending').all()

def test_v4_query_evidence():
    evidence=json.loads((ROOT/'data/results/v4_query_evidence.json').read_text())
    assert evidence['source_sha256']==registry()['V4']['source_sha256']
    assert len(evidence['explorer_checks'])==4
    assert all(c['passed'] and c['preview_rows']==min(c['reference_count'],c['limit']) for c in evidence['explorer_checks'])

@pytest.mark.skipif(not os.getenv('STB_TEST_V4'),reason='Set STB_TEST_V4 to the actual V4 Parquet for source verification')
def test_actual_v4_source():
    path=Path(os.environ['STB_TEST_V4']);meta=registry()['V4']
    with path.open('rb') as handle:assert hashlib.file_digest(handle,'sha256').hexdigest()==meta['source_sha256']
    evidence=json.loads((ROOT/'data/results/v4_query_evidence.json').read_text())
    for check in evidence['explorer_checks']:
        frame=preview(path,check['filters'],check['limit'],meta['column_map'],meta['mode_map'])
        assert len(frame)==min(check['reference_count'],check['limit'])
        for field,value in check['filters'].items():assert frame[field].astype(str).eq(str(value)).all()
        if frame.actual_arrival.str.contains(' ').all():
            import pandas as pd
            expected=(pd.to_datetime(frame.actual_arrival)-pd.to_datetime(frame.scheduled_arrival)).dt.total_seconds()/60
            assert (frame.arrival_delay_minutes-expected).abs().lt(1e-8).all()
    assert len(preview(path,{},999999,meta['column_map'],meta['mode_map']))==2000
    time_only=preview(path,{'mode':'Bus','service_date':'2026-10-05'},20,meta['column_map'],meta['mode_map'])
    assert not time_only.empty
    assert time_only.scheduled_arrival.str.fullmatch(r'\d{2}:\d{2}:\d{2}').all()
    assert time_only.arrival_delay_minutes.isna().all()
