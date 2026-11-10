"""Create deterministic synthetic examples, schemas and brief-supplied findings."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from services.data_loader import ROOT, SCHEMAS, INTEGRATED

def main():
    for directory in ['data/results','data/demo','data/integrated','data/gtfs','data/templates']:
        (ROOT/directory).mkdir(parents=True,exist_ok=True)
    for kind, columns in SCHEMAS.items():
        pd.DataFrame(columns=columns).to_csv(ROOT/f'data/templates/{kind}.csv',index=False)
    pd.DataFrame(columns=INTEGRATED).to_csv(ROOT/'data/templates/integrated.csv',index=False)
    base={'dataset_version':'V1','synthetic':False,'provenance':'User-supplied frozen V1 benchmark','updated':'Not supplied'}
    pd.DataFrame([{**base,'model':model,'mae':value} for model,value in [('Zero-delay baseline',2.634),('Mode-median baseline',2.372),('Route-hour median baseline',2.316),('LightGBM',2.764)]]).to_csv(ROOT/'data/results/delay.csv',index=False)
    pd.DataFrame([{**base,'model':model,'accuracy':acc,'macro_f1':f1} for model,acc,f1 in [('Majority-class baseline',.5943,.0439),('Decision tree',.5984,.0729)]]).to_csv(ROOT/'data/results/occupancy.csv',index=False)
    quality=[]
    checks=[('Raw records',5419264,'records','Deduplication','October; year not supplied','All sources; mode allocation not supplied'),('Retained records',5377510,'records','Deduplication','October; year not supplied','All sources; mode allocation not supplied'),('Removed by source-aware deduplication',41754,'records','Deduplication','October; year not supplied','All sources; mode allocation not supplied'),('Missing scheduled arrivals',5144,'records','Missing values','Quality-check scope not supplied','Not supplied'),('Missing actual arrivals',3069,'records','Missing values','Quality-check scope not supplied','Not supplied'),('Repeated-key groups without distinct timestamps',6822,'groups','Duplicate keys','Quality-check scope not supplied','Not supplied'),('Occupancy-disagreement groups',463,'groups','Conflicting keys','Quality-check scope not supplied','Not supplied'),('Conflicting trip-stop keys flagged',60,'groups','Conflicting keys','Quality-check scope not supplied','Not supplied'),('Potential service-date rollover anomalies',1678,'records','Timestamp anomalies','Quality-check scope not supplied','Bus / BOAM')]
    for metric,value,unit,category,scope,mode in checks:
        quality.append(dict(dataset_version='V3',mode=mode,start_date='',end_date='',scope=scope,category=category,metric=metric,value=value,unit=unit,status='Preliminary / unresolved',synthetic=False,provenance='User-supplied preliminary V3 findings; scopes may overlap',updated='Not supplied'))
    pd.DataFrame(quality).to_csv(ROOT/'data/results/quality.csv',index=False)
    aggregates=[]; benchmarks=[]; integrated=[]
    for version in ['V1','V3','V4']:
        for i,mode in enumerate(['Bus','Ferry','Light rail','Rail']):
            for day in range(1,15):
                n=1000+(i+1)*137+day*31
                aggregates.append(dict(dataset_version=version,mode=mode,service_date=f'2025-10-{day:02}',records=n,missing_scheduled=i+2,missing_actual=i+1,gtfs_matches=n-30,gtfs_eligible=n,synthetic=True,provenance='Deterministic illustrative example',updated='Example only'))
            for fmt,size in [('CSV',120),('Parquet',32)]:
                for rep in range(1,4):
                    benchmarks.append(dict(dataset_version=version,mode=mode,category='Aggregation',format=fmt,workload='Mode count',records=100000,size_mb=size,seconds=(.25 if fmt=='CSV' else .08)+rep*.005,repetition=rep,hardware='Illustrative environment — not measured',software='Illustrative only',synthetic=True,provenance='Synthetic demonstration',updated='Example only'))
    for i in range(600):
        mode=['Bus','Ferry','Light rail','Rail'][i%4]
        scheduled=pd.Timestamp('2025-10-01 08:00')+pd.Timedelta(minutes=i)
        actual=scheduled+pd.Timedelta(minutes=i%13-3)
        integrated.append(dict(dataset_version='DEMO',source='SYNTHETIC',mode=mode,service_date='2025-10-01',route_id=f'DEMO-{i%4}',trip_id=f'DEMO-TRIP-{i//20}',direction_id=str(i%2),stop_id=f'DEMO-STOP-{i%20}',stop_sequence=i%20+1,scheduled_arrival=scheduled,actual_arrival=actual,arrival_delay_minutes=i%13-3,occupancy_band='0–20 passengers' if mode=='Light rail' else None,gtfs_route_id=None,gtfs_stop_id=None,quality_flags='SYNTHETIC'))
    pd.DataFrame(aggregates).to_csv(ROOT/'data/demo/aggregates.csv',index=False)
    pd.DataFrame(benchmarks).to_csv(ROOT/'data/demo/benchmarks.csv',index=False)
    pd.DataFrame(integrated).to_parquet(ROOT/'data/demo/integrated.parquet',index=False)

if __name__=='__main__': main()
