"""Local, provenance-preserving input adapters. No network access is required."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
 'quality': ['dataset_version','mode','start_date','end_date','scope','category','metric','value','unit','status','synthetic','provenance','updated'],
 'aggregates': ['dataset_version','mode','service_date','records','missing_scheduled','missing_actual','gtfs_matches','gtfs_eligible','synthetic','provenance','updated'],
 'delay': ['dataset_version','model','mae','synthetic','provenance','updated'],
 'occupancy': ['dataset_version','model','accuracy','macro_f1','synthetic','provenance','updated'],
 'benchmarks': ['dataset_version','mode','category','format','workload','records','size_mb','seconds','repetition','hardware','software','synthetic','provenance','updated'],
 'predictions': ['dataset_version','model','actual_delay','predicted_delay','synthetic','provenance','updated'],
 'bands': ['dataset_version','band','count','synthetic','provenance','updated'],
 'confusion': ['dataset_version','model','actual_band','predicted_band','count','synthetic','provenance','updated'],
 'distance': ['dataset_version','model','band_distance','count','synthetic','provenance','updated'],
 'stops': ['stop_id','stop_name','stop_lat','stop_lon','provenance'],
}
INTEGRATED = ['dataset_version','source','mode','service_date','route_id','trip_id','direction_id','stop_id','stop_sequence','scheduled_arrival','actual_arrival','arrival_delay_minutes','occupancy_band','gtfs_route_id','gtfs_stop_id','quality_flags']

def config(name: str) -> dict:
    return json.loads((ROOT / 'config' / f'{name}.json').read_text(encoding='utf-8'))

def registry() -> dict:
    result = config('datasets')
    for version, meta in result.items():
        if not isinstance(meta.get('validated'), bool):
            raise ValueError(f'{version}: validated must be an explicit boolean')
        if meta.get('status') == 'validated' and not meta['validated']:
            raise ValueError('Validated status requires validated=true')
    return result

def version_label(version: str, meta: dict) -> str:
    if meta.get('validated') is True:
        return f'Validated {version}'
    return {'frozen':f'Frozen {version}','provisional':f'Provisional {version}'}.get(meta['status'], f'{version} Candidate — awaiting validation')

def validate(frame: pd.DataFrame, kind: str) -> pd.DataFrame:
    missing = set(SCHEMAS[kind]) - set(frame.columns)
    if missing:
        raise ValueError(f'{kind}: missing columns {sorted(missing)}')
    if 'synthetic' in frame:
        normalized = frame.synthetic.astype(str).str.lower()
        if not normalized.isin(['true','false']).all():
            raise ValueError('synthetic must be true or false')
        frame = frame.copy()
        frame['synthetic'] = normalized.eq('true')
    for col in {'mae','rmse','within_5','accuracy','macro_f1','value','records','seconds','size_mb','count','actual_delay','predicted_delay','stop_lat','stop_lon'} & set(frame):
        frame[col] = pd.to_numeric(frame[col], errors='raise')
    for col in {'accuracy','macro_f1','within_5'} & set(frame):
        if not frame[col].dropna().between(0,1).all():
            raise ValueError(f'{col} must be a fraction between 0 and 1')
    return frame

def read_file(path: Path, kind: str) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=SCHEMAS[kind])
    frame = pd.read_json(path) if path.suffix.lower() == '.json' else pd.read_csv(path)
    return validate(frame, kind)

def load(kind: str, version: str, mode: str) -> pd.DataFrame:
    """Research inputs are always loaded separately from demonstration inputs."""
    meta = registry()[version]
    path = ROOT / meta.get(kind, f'data/results/{kind}.csv')
    frame = read_file(path, kind)
    if 'dataset_version' in frame:
        frame = frame[frame.dataset_version == version]
    if 'synthetic' in frame:
        frame = frame[~frame.synthetic]
    return frame

def demo(kind: str, version: str) -> pd.DataFrame:
    frame = read_file(ROOT / 'data/demo' / f'{kind}.csv', kind)
    if 'synthetic' in frame and not frame.synthetic.all():
        raise ValueError('Demo files must contain only synthetic rows')
    return frame[frame.dataset_version == version] if 'dataset_version' in frame else frame
