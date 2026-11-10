"""Reproducible, offline V4 aggregates and explorer verification from source Parquet."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import duckdb
from services.data_loader import ROOT
from services.duckdb_queries import preview

MODE_MAP={'BOAM':'Bus','FOAM':'Ferry','LOAM':'Light rail','ROAM':'Rail'}
COLUMN_MAP={'source':'source_dataset','trip_id':'source_trip_id','direction_id':'direction','occupancy_band':'occupancy_range'}

def build(source: Path, output: Path) -> dict:
    """Full-source SQL scans; only compact aggregates and verification evidence leave DuckDB."""
    updated=datetime.now(timezone.utc).isoformat()
    with source.open('rb') as handle:
        digest=hashlib.file_digest(handle,'sha256').hexdigest()
    output.mkdir(parents=True,exist_ok=True)
    with duckdb.connect() as con:
        con.execute('CREATE VIEW raw AS SELECT * FROM read_parquet('+"'"+str(source).replace("'","''")+"')")
        actual_modes=[r[0] for r in con.execute('select distinct mode from raw').fetchall()]
        if set(actual_modes)-set(MODE_MAP): raise ValueError(f'Unmapped modes: {actual_modes}')
        modes="CASE mode "+' '.join(f"WHEN '{k}' THEN '{v}'" for k,v in MODE_MAP.items())+' END'
        daily=con.execute(f'''SELECT 'V4' dataset_version,{modes} AS "mode",service_date,
          count(*) records,count(*) FILTER(WHERE scheduled_arrival IS NULL OR trim(scheduled_arrival)='') missing_scheduled,
          count(*) FILTER(WHERE actual_arrival IS NULL OR trim(actual_arrival)='') missing_actual,
          count(*) FILTER(WHERE gtfs_trip_id IS NOT NULL AND trim(gtfs_trip_id)!='') gtfs_matches,
          count(*) gtfs_eligible FROM raw GROUP BY mode, service_date ORDER BY mode,service_date''').df()
        daily['synthetic']=False;daily['provenance']=f'Full V4 SQL aggregation; SHA256 {digest}';daily['updated']=updated
        daily.to_csv(output/'v4_aggregates.csv',index=False)
        coverage=con.execute('''SELECT mode,count(*) records,min(service_date)::VARCHAR start_date,max(service_date)::VARCHAR end_date,
          count(distinct route_id) unique_routes,count(distinct stop_id) unique_stops,
          count(*) FILTER(WHERE service_date IS NULL) missing_service_date,
          count(distinct service_date) observed_service_dates,
          count(*) FILTER(WHERE try_cast(scheduled_arrival AS TIME) IS NOT NULL AND try_cast(scheduled_arrival AS TIMESTAMP) IS NULL) scheduled_time_only,
          count(*) FILTER(WHERE try_cast(actual_arrival AS TIME) IS NOT NULL AND try_cast(actual_arrival AS TIMESTAMP) IS NULL) actual_time_only
          FROM raw GROUP BY mode ORDER BY mode''').df().to_dict(orient='records')
        for row in coverage:row['mode']=MODE_MAP[row['mode']]
        total=con.execute('''select count(*), count(distinct (mode,route_id)) filter(where route_id is not null),
          count(distinct (mode,stop_id)) filter(where stop_id is not null),min(service_date)::varchar,max(service_date)::varchar from raw''').fetchone()
        checks=[]
        for row in coverage:
            source_mode=next(k for k,v in MODE_MAP.items() if v==row['mode'])
            sample=con.execute('select route_id,direction,stop_id,service_date::varchar from raw where mode=? and route_id is not null and stop_id is not null limit 1',[source_mode]).fetchone()
            if not sample:raise ValueError('No filterable example for '+source_mode)
            filters=dict(zip(['route_id','direction_id','stop_id','service_date'],sample));filters['mode']=row['mode']
            result=preview(source,filters,37,COLUMN_MAP,MODE_MAP)
            expected=con.execute('''select count(*) from raw where mode=? and cast(route_id as varchar)=? and cast(direction as varchar)=? and cast(stop_id as varchar)=? and cast(service_date as varchar)=?''',[source_mode,*sample]).fetchone()[0]
            assert len(result)==min(expected,37)
            assert result['mode'].eq(row['mode']).all()
            for field,value in filters.items():assert result[field].astype(str).eq(str(value)).all()
            checks.append({'mode':row['mode'],'filters':filters,'reference_count':expected,'preview_rows':len(result),'limit':37,'passed':True})
        assert preview(source,{'route_id':"' OR 1=1 --"},20,COLUMN_MAP,MODE_MAP).empty
        assert len(preview(source,{},100000,COLUMN_MAP,MODE_MAP))==2000
        assert int(daily.records.sum())==total[0]==sum(r['records'] for r in coverage)
    report={'dataset_version':'V4','source_file':source.name,'source_sha256':digest,'source_bytes':source.stat().st_size,'generated_at':updated,'records':total[0],'unique_routes':total[1],'unique_stops':total[2],'date_coverage':f'{total[3]} to {total[4]}','coverage_definition':'Unique routes and stops counted as (mode, ID) pairs; service-date coverage, not continuous availability.','mode_totals':coverage,'gtfs_metric_label':'GTFS trip ID populated / records (not independently revalidated GTFS matches)','explorer_checks':checks,'injection_check_passed':True,'release_validation':'Not established by these aggregate and query checks'}
    (output/'v4_query_evidence.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args()
    print(json.dumps(build(args.source,ROOT/'data/results'),indent=2))
