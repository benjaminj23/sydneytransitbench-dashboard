from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import pytest
from services.data_loader import registry,version_label,load,demo,read_file,validate,ROOT
from services.duckdb_queries import preview

def test_registry():
    assert registry()['V3']['records']==7343136
    assert registry()['V4']['validated'] is True

def test_labels():
    for version,meta in registry().items():
        assert 'Validated' not in version_label(version,meta)
    assert version_label('V4',{'validated':True,'status':'validated'})=='Validated V4'
    assert version_label('V4',registry()['V4'])=='Frozen V4'

def test_missing(tmp_path):
    assert read_file(tmp_path/'missing.csv','delay').empty
    with pytest.raises(FileNotFoundError): preview(tmp_path/'missing.parquet',{})

def test_schema():
    with pytest.raises(ValueError): validate(pd.DataFrame({'model':['x']}),'delay')

def test_metrics_and_versions():
    data=load('delay','V1','demo')
    assert data.loc[data.model=='Route-hour median baseline','mae'].iloc[0]==2.316
    assert load('delay','V3','demo').empty
    assert load('occupancy','V1','real').macro_f1.max()==.0729

def test_demo_separation():
    assert demo('aggregates','V3').synthetic.all()
    assert not load('quality','V3','demo').synthetic.any()
    assert load('benchmarks','V3','real').empty

def test_limits_and_filters():
    path=ROOT/'data/demo/integrated.parquet'
    assert len(preview(path,{},17))==17
    assert len(preview(path,{},0))==1
    frame=preview(path,{'mode':'Ferry'},20)
    assert frame['mode'].eq('Ferry').all()
    assert preview(path,{'route_id':"' OR 1=1 --"},20).empty
    with pytest.raises(ValueError): preview(path,{'unsafe':'x'})

def test_scopes():
    q=load('quality','V3','real')
    assert q.loc[q.metric=='Raw records','scope'].iloc[0]=='October; year not supplied'
    assert q.start_date.isna().all()
