"""Bounded projections with parameterized predicates; each query owns its connection."""
from pathlib import Path
import duckdb
from services.data_loader import INTEGRATED

FILTERS = ['mode','route_id','direction_id','stop_id','service_date']

def preview(path: Path, filters: dict, limit: int = 500):
    limit = max(1, min(int(limit), 2000))
    if not path.exists():
        raise FileNotFoundError(f'Integrated Parquet unavailable: {path.name}')
    with duckdb.connect() as con:
        columns = {r[0] for r in con.execute('DESCRIBE SELECT * FROM read_parquet(?)', [str(path)]).fetchall()}
        selected = [c for c in INTEGRATED if c in columns]
        if not selected:
            raise ValueError('Parquet has no recognized integrated columns')
        clauses, params = [], [str(path)]
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
        return con.execute(f'SELECT {projection} FROM read_parquet(?){where} LIMIT ?', params + [limit]).df()
