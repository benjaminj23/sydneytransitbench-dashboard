"""Bounded projections with parameterized predicates; each query owns its connection."""
from pathlib import Path
import duckdb
from services.data_loader import INTEGRATED

FILTERS = ['mode','route_id','direction_id','stop_id','service_date']

def preview(path: Path, filters: dict, limit: int = 500, column_map: dict | None = None, mode_map: dict | None = None):
    limit = max(1, min(int(limit), 2000))
    if not path.exists():
        raise FileNotFoundError(f'Integrated Parquet unavailable: {path.name}')
    with duckdb.connect() as con:
        columns = {r[0] for r in con.execute('DESCRIBE SELECT * FROM read_parquet(?)', [str(path)]).fetchall()}
        mapping = column_map or {}
        for alias,original in mapping.items():
            if alias not in INTEGRATED or original not in columns:
                raise ValueError(f'Invalid configured column mapping: {alias} → {original}')
        projection=[]
        for alias in INTEGRATED:
            original=mapping.get(alias,alias)
            if original in columns:
                quoted='"'+original.replace('"','""')+'"'
                if alias=='mode' and mode_map:
                    quoted='CASE '+quoted+' '+ ' '.join("WHEN '"+k.replace("'","''")+"' THEN '"+v.replace("'","''")+"'" for k,v in mode_map.items())+' ELSE '+quoted+' END'
                projection.append(quoted+' AS "'+alias+'"')
        if {'scheduled_arrival','actual_arrival'}.issubset(columns) and 'arrival_delay_minutes' not in columns:
            projection.append('epoch(try_cast(actual_arrival AS TIMESTAMP)-try_cast(scheduled_arrival AS TIMESTAMP))/60.0 AS arrival_delay_minutes')
        con.execute('CREATE VIEW normalized AS SELECT '+','.join(projection)+' FROM read_parquet('+"'"+str(path).replace("'","''")+"')")
        columns={r[0] for r in con.execute('describe normalized').fetchall()}
        selected = [c for c in INTEGRATED if c in columns]
        if not selected:
            raise ValueError('Parquet has no recognized integrated columns')
        clauses, params = [], []
        for key, value in filters.items():
            if key not in FILTERS:
                raise ValueError('Unsupported filter')
            if value:
                if key not in columns:
                    raise ValueError(f'Filter column unavailable: {key}')
                clauses.append(f'CAST("{key}" AS VARCHAR) = ?')
                params.append(str(value))
        where = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
        projection = ','.join(f'"{c}"' for c in selected)
        return con.execute(f'SELECT {projection} FROM normalized{where} LIMIT ?', params + [limit]).df()
