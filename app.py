"""SydneyTransitBench — local research presentation and integration workbench."""
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from services.data_loader import ROOT, config, registry, version_label, load, demo, read_file, validate, integrated_path
from services.duckdb_queries import preview
from components.ui import style, chart, table, DEMO_LABEL
from components.cockpit import hero, mode_selector

st.set_page_config(page_title='SydneyTransitBench', page_icon='🚉', layout='wide')
style()
settings = config('settings')
versions = registry()
PAGES = ['Executive Overview','Data Quality and Validation','Transport Network Explorer','Arrival Delay Prediction','Occupancy Prediction','Storage and Query Performance','About the Research']
with st.sidebar:
    st.markdown('### SydneyTransitBench')
    st.caption('THE NETWORK, EXPLAINED.')
    workspace = st.radio('Workspace', ['Dashboard','Explore','Research'])
    with st.expander('Dataset settings', expanded=False):
        version = st.selectbox('Dataset version', list(versions), index=list(versions).index(settings['default_version']))
        mode = st.selectbox('Data mode', ['demo','real'], index=0 if os.getenv('STB_MODE',settings['mode']) == 'demo' else 1)
    meta = versions[version]
    st.info(version_label(version,meta))
    st.caption('Integrating operational transport data to study quality, prediction and analytical performance.')
    st.divider()
    st.caption('UNSW | Master of Data Science and Decisions | SydneyTransitBench')

page = PAGES[0] if workspace=='Dashboard' else PAGES[2] if workspace=='Explore' else None
st.caption(f'SYDNEY TRANSIT INTELLIGENCE  /  {version_label(version, meta)}  /  {mode.upper()}')
selected_transport = mode_selector()
if workspace=='Dashboard':
    hero(selected_transport,version,version_label(version,meta))
elif workspace=='Research':
    page = st.selectbox('Research topic',[PAGES[i] for i in [1,3,4,5,6]])
    st.title(page)
else:
    st.title(f'{selected_transport} explorer')
if mode == 'demo':
    st.info('Demo mode: supplied research findings retain their provenance. Synthetic charts are labelled individually.')
st.caption(f"Provenance: {meta['provenance']} · Last updated: {meta['updated']}")
context = (version, mode, selected_transport)
if st.session_state.get('explorer_context') != context:
    st.session_state.pop('explorer_result', None)
    st.session_state.pop('explorer_synthetic', None)
    st.session_state['explorer_context'] = context

def get(kind):
    try:
        return load(kind,version,mode)
    except (ValueError, OSError, KeyError) as exc:
        st.error(f'{kind} input could not be loaded: {exc}')
        return pd.DataFrame()

def absent(message):
    st.info('Awaiting data · ' + message)

def aggregates():
    data = get('aggregates')
    if data.empty and mode == 'demo' and meta.get('allow_demo',True):
        data = demo('aggregates',version)
    if not data.empty:
        data = data[data['mode']==selected_transport]
    return data

def notes(text):
    with st.expander('Research methodology and interpretation'):
        st.write(text)

PIPELINE = 'Raw operational data → Timestamp standardisation → Source-aware deduplication → Common schema → GTFS matching → Data-quality validation → Parquet analytical outputs'

def occupancy_validation_context():
    run = meta.get('occupancy_validation')
    if run:
        st.info(f"LOAM validation only: {run['training_service_dates']} training service dates and {run['validation_service_dates']} validation service dates. Exact dates and experiment artifacts have not been supplied. Independent test pending.")
        st.caption(f"Earlier reported macro F1: {run['earlier_macro_f1']:.4f}. Shown for context; its split and direct comparability have not been established.")

if page == PAGES[0]:
    cols = st.columns(4)
    cols[0].metric('Integrated records · all modes', f"{meta['records']:,}" if meta['records'] is not None else 'Not supplied')
    cols[1].metric('Exploring', selected_transport)
    cols[2].metric('Dataset', version)
    cols[3].metric('Release status', meta['status'].title())
    if qa := meta.get('release_qa'):
        st.success(f"Published benchmark · {meta['schema_columns']} unified columns · Independent QA complete")
        with st.expander('Release QA and known limitations'):
            st.write(f"Critical checks passed. {qa['loam_cross_source_removed']:,} redundant cross-source light-rail records removed; {qa['loam_cross_source_remaining']} cross-source LOAM overlaps remain. {qa['retained_exact_duplicate_copies']} exact duplicate copies were retained.")
            st.caption('The project freeze is a versioning decision. Azure storage-level immutability has not been confirmed. GTFS matching limitations are documented in the release.')
            st.caption(f"Team-confirmed Azure release: `{meta['azure_blob_path']}`. Companion artifacts: {', '.join(qa['artifacts'])}. These private artifacts were reported by the team and were not read by this deployment.")
    if meta.get('mode_totals'):
        st.subheader('V4 coverage · queried from the source Parquet')
        st.dataframe(pd.DataFrame(meta['mode_totals']),hide_index=True,use_container_width=True)
        st.caption(meta['coverage_definition'])
        st.caption(f"Aggregate generation: {meta['updated']} · Source SHA-256: {meta['source_sha256']}")
        selected_coverage=next((r for r in meta['mode_totals'] if r['mode']==selected_transport),None)
        if selected_coverage and selected_coverage.get('scheduled_time_only',0):
            st.info('This mode contains time-only arrival strings. Delay derivation is left unavailable for those rows until service-date and rollover rules are confirmed; these values are not automatically labelled errors.')
    st.subheader(f'Inside the {selected_transport.lower()} network')
    st.caption('Mode selection filters the charts below. Research totals and model evaluations retain their original scope.')
    data = aggregates()
    if not data.empty:
        chart(data,kind='area',x='service_date',y='records',color='mode',title=f'{selected_transport} · operational record volume')
        a,b = st.columns(2)
        with a:
            missing = data.groupby(['mode','synthetic'],as_index=False)[['missing_scheduled','missing_actual']].sum()
            chart(missing, x='mode',y=['missing_scheduled','missing_actual'],title='Arrival timestamp completeness · missing values')
        eligible = data.groupby(['mode','synthetic'],as_index=False)[['gtfs_matches','gtfs_eligible']].sum()
        eligible['match_rate'] = eligible.gtfs_matches.div(eligible.gtfs_eligible.replace(0,float('nan')))
        with b: chart(eligible,x='mode',y='match_rate',color='mode',title=meta.get('gtfs_metric_label','GTFS matching rate (matched / eligible)'))
    else: absent('Supply aggregates.csv for mode counts, dates, missingness and GTFS rates.')
    with st.expander('Coverage, provenance and integration pipeline'):
        st.write(PIPELINE)
        st.write({label:meta.get(key,'Not supplied') for label,key in [('Unique routes','unique_routes'),('Unique stops','unique_stops'),('Date coverage','date_coverage')]})
        st.caption('Arrival-delay distributions await observed delay aggregates. No live vehicle positions are shown.')
    notes('V4 totals and coverage are direct SQL results from the fingerprinted source Parquet. Older registry totals are project-reported. Route and stop identifiers are counted within mode, not deduplicated physical entities across modes. Service-date bounds do not imply continuous date coverage. Synthetic aggregates are never used for research KPI cards. Frozen does not imply validated.')
    st.subheader('Modelling results · evaluation register')
    st.caption('Metrics stay attached to their evaluated dataset. Evaluation dates are separate from file update dates.')
    for task in ['delay','occupancy']:
        evaluations=get(task)
        if evaluations.empty:
            st.info(f'{version} {task}: experiments awaiting team-supplied evaluation results, dates, baselines and limitations.')
        else:
            display=evaluations.copy()
            for field in ['evaluation_start','evaluation_end','evaluated_at','split_strategy','baseline','limitations']:
                if field not in display:display[field]='Not supplied'
            fields=['model']+(['mae'] if task=='delay' else ['accuracy','macro_f1'])+['evaluation_start','evaluation_end','evaluated_at','split_strategy','baseline','limitations']
            if task=='occupancy' and meta.get('occupancy_validation'):
                st.write(f'{version} · LOAM occupancy validation')
                occupancy_validation_context()
                fields=['model','macro_f1','accuracy','band_mae']
                display['accuracy']=display['accuracy'].map(lambda value:f'{value:.2%}' if pd.notna(value) else 'Not supplied')
                display['band_mae']=display['band_mae'].map(lambda value:f'{value:.4f}' if pd.notna(value) else 'Not supplied')
            else: st.write(f'{version} · {task}')
            st.dataframe(display[fields],hide_index=True,use_container_width=True)
    st.subheader('From the integration pipeline to predictive modelling')
    st.write('Predictive modelling is a downstream evaluation of the unified dataset’s analytical usefulness. The pipeline turns source-specific records into comparable trip-stop observations. Deduplication and timestamp checks determine which observations are eligible; consistent route, stop, direction and schedule fields make it possible to build the same features across sources.')
    st.write('LOAM occupancy provides a concrete example: the unified table supplies scheduled features and observed passenger bands, which serve as labels. Comparing a unified historical model with separate route models on held-out service dates tests whether the integrated data supports useful predictions across routes. The current validation is light rail only and does not establish independent test performance or generalisation across modes.')
    st.caption('This is the link requested by Reviewer 1: the pipeline produces the benchmark and its eligibility rules; modelling evaluates what that benchmark can support. Dataset QA and predictive performance answer different questions.')

elif page == PAGES[1]:
    st.warning('Quality checks may overlap and cover different scopes. Do not sum these findings or extrapolate October figures to all of V3. Flagged anomalies are not confirmed errors.')
    data = get('quality')
    if not data.empty:
        a,b = st.columns(2)
        selected_mode = a.selectbox('Transport mode',['All']+sorted(data['mode'].unique().tolist()))
        category = b.selectbox('Quality-check category',['All']+sorted(data.category.unique().tolist()))
        if selected_mode != 'All': data = data[data['mode']==selected_mode]
        if category != 'All': data = data[data.category==category]
        known = pd.to_datetime(data.start_date,errors='coerce').dropna()
        if not known.empty:
            bounds = st.date_input('Scope dates overlap this range',value=(known.min().date(),pd.to_datetime(data.end_date,errors='coerce').max().date()))
            if len(bounds)==2:
                starts = pd.to_datetime(data.start_date,errors='coerce'); ends = pd.to_datetime(data.end_date,errors='coerce')
                data = data[starts.isna() | ((starts <= pd.Timestamp(bounds[1])) & (ends >= pd.Timestamp(bounds[0])))]
        for offset in range(0,len(data),3):
            for col,(_,row) in zip(st.columns(3),data.iloc[offset:offset+3].iterrows()):
                col.metric(row.metric,f'{row.value:,.0f}' if row.unit=='records' or row.unit=='groups' else str(row.value))
                col.caption(f'{row.scope} · {row["mode"]} · {row.status}')
        st.subheader('Scoped quality register')
        table(data)
        st.subheader('Diagnostics by check scope')
        scope = st.selectbox('Diagnostic scope',data.scope.unique()) if not data.empty else None
        scoped = data[data.scope==scope]
        for cat in scoped.category.unique():
            chart(scoped[scoped.category==cat],x='metric',y='value',color='mode',title=f'{cat} — {scope}; categories may overlap')
    else: absent('Supply scoped quality.csv. No research findings are supplied for this version.')
    agg = aggregates()
    if not agg.empty:
        st.subheader('Mode-level diagnostic aggregates')
        chart(agg,x='mode',y=['missing_scheduled','missing_actual'],title='Missing values by mode')
        agg = agg.copy(); agg['gtfs_rate'] = agg.gtfs_matches / agg.gtfs_eligible.replace(0,float('nan'))
        chart(agg,x='mode',y='gtfs_rate',color='mode',title=meta.get('gtfs_metric_label','GTFS matches / eligible records'))
    absent('Supply scoped GTFS rates and source-level quality rows where unavailable. Unknown rates remain unknown.')
    notes('Raw and retained counts refer to the stated source/time scope. Deduplication removed = raw − retained within the same scope. Missing-arrival counts identify null timestamps. Repeated-key groups, occupancy disagreements and conflicting keys use different tests; they are not additive. Potential rollover anomalies require adjudication. GTFS rate uses eligible records as its denominator. Scope dates without a year are retained as text descriptions rather than invented dates.')

elif page == PAGES[2]:
    st.write('Query a bounded operational preview. Exact filters are pushed into DuckDB; blank filters mean all values.')
    raw_available=integrated_path(version,meta).exists()
    explorer_available=raw_available or (mode=='demo' and meta.get('allow_demo',True))
    if not explorer_available:
        st.info(f'{version} raw Parquet is not available in this deployment. The charts use precomputed aggregates; they do not establish access to raw records. Configure the approved dataset path to enable queries.')
    with st.form('explorer'):
        cols = st.columns(5)
        filters = {'mode':selected_transport}
        cols[0].metric('Transport mode',selected_transport)
        filters.update({key:col.text_input(label) for col,key,label in zip(cols[1:],['route_id','direction_id','stop_id','service_date'],['Route ID','Direction','Stop ID','Service date (YYYY-MM-DD)'])})
        limit = st.slider('Maximum preview rows',10,2000,500)
        run = st.form_submit_button('Query operational records',type='primary',disabled=not explorer_available)
    if run:
        path = integrated_path(version,meta)
        synthetic = False
        if not path.exists() and mode=='demo' and meta.get('allow_demo',True):
            path = ROOT / 'data/demo/integrated.parquet'; synthetic=True
        try:
            @st.cache_data(ttl=120,max_entries=32)
            def cached_preview(path_string,mtime,filters,limit,column_map,mode_map):
                return preview(Path(path_string),filters,limit,column_map,mode_map)
            if meta.get('source_sha256'):
                import hashlib
                @st.cache_data(max_entries=4)
                def source_digest(path_string,mtime,size):
                    with open(path_string,'rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()
                if source_digest(str(path),path.stat().st_mtime_ns,path.stat().st_size)!=meta['source_sha256']:
                    raise ValueError('Source fingerprint differs from the V4 aggregate release. Regenerate and review the release artifacts before querying.')
            result = cached_preview(str(path),path.stat().st_mtime_ns,filters,limit,meta.get('column_map',{}),meta.get('mode_map',{}))
            if synthetic: st.warning(DEMO_LABEL)
            st.session_state['explorer_result'] = result
            st.session_state['explorer_synthetic'] = synthetic
        except (OSError,ValueError,Exception) as exc:
            st.error(f'Could not query operational data: {exc}')
            st.session_state.pop('explorer_result',None)
    if 'explorer_result' in st.session_state:
        if st.session_state.get('explorer_synthetic'): st.warning(DEMO_LABEL)
        result = st.session_state['explorer_result']
        st.caption(f'{len(result):,} rows; preview is not a population summary.')
        table(result)
        try:
            stops = read_file(ROOT / meta.get('stops','data/gtfs/stops.csv'),'stops')
            if 'stop_id' in result:
                stops = stops[stops.stop_id.astype(str).isin(result.stop_id.astype(str))]
            stops = stops[stops.stop_lat.between(-90,90)&stops.stop_lon.between(-180,180)]
            if not stops.empty: st.map(stops.rename(columns={'stop_lat':'latitude','stop_lon':'longitude'}))
            else: absent('Load verified GTFS stop coordinates to show selected stop locations. No coordinates are invented.')
        except (ValueError,OSError) as exc: st.error(str(exc))
    notes('Only recognized fields are selected. Queries use bound parameters and a hard 2,000-row limit; the preview is unordered and not a random sample. GTFS maps show stop points, not inferred route geometry. Timestamp columns should be timezone-consistent. Delay is actual minus scheduled arrival in minutes.')
    if version=='V4':
        st.caption('V4 explorer was tested against the fingerprinted local source with mode + route + direction + stop + service-date filters and independent SQL reference counts. The hosted explorer requires that same Parquet source; bundled aggregate charts do not imply hosted raw-data availability.')

elif page in [PAGES[3],PAGES[4]]:
    delay = page == PAGES[3]
    st.caption('Evaluation scope: all transport modes in the supplied delay benchmark.' if delay else 'Evaluation scope: light rail only, regardless of the network selector above.')
    kind = 'delay' if delay else 'occupancy'
    if not delay:
        occupancy_validation_context()
    st.subheader('Regression · arrival delay in minutes' if delay else 'Multiclass classification · 22 ordered passenger-count bands')
    st.write('Observed delay = actual arrival − scheduled arrival. Positive is late; negative is early. Predicted arrival = scheduled arrival + predicted delay.' if delay else 'Predict the reported passenger-count band at each light-rail stop. Confirmed examples: 0–20 and 21–40 passengers. The remaining band labels must come from the research data.')
    data = get(kind)
    with st.expander('Preview a model-results CSV or JSON'):
        uploaded = st.file_uploader('Research results file (schema in INTEGRATION.md)',type=['csv','json'],key=kind+'_upload')
        if uploaded is not None:
            try:
                incoming = pd.read_json(uploaded) if uploaded.name.lower().endswith('.json') else pd.read_csv(uploaded)
                incoming = validate(incoming,kind)
                incoming = incoming[(incoming.dataset_version==version)&(~incoming.synthetic)]
                if incoming.empty:
                    st.info('No non-synthetic results match the selected dataset version.')
                else:
                    data = incoming
                    st.caption('Uploaded preview only; no local research files are overwritten.')
            except (ValueError,TypeError) as exc:
                st.error(f'Results file rejected: {exc}')
    st.caption(f'Only results explicitly associated with {version} are shown. Selecting another dataset never transfers V1 results.')
    if not data.empty:
        metrics = ['mae','rmse','within_5'] if delay else ['accuracy','macro_f1'] + (['band_mae'] if 'band_mae' in data else [])
        for metric in metrics:
            if metric in data and data[metric].notna().any():
                unit = 'minutes' if metric in ['mae','rmse'] else 'bands' if metric=='band_mae' else 'fraction'
                scope = 'Validation · ' if not delay and meta.get('occupancy_validation') else ''
                chart(data,x='model',y=metric,color='model',title=f'{scope}{metric.upper()} ({unit})')
            else: absent(f'Supply {metric} in {kind}.csv.')
        if delay:
            valid = data.dropna(subset=['mae'])
            if not valid.empty:
                best = valid.loc[valid.mae.idxmin()]
                st.success(f'Lowest available MAE: {best.model} · {best.mae:.3f} minutes. This comparison does not establish universal optimality.')
        table(data)
    else: absent(f'No {kind} evaluation results supplied for {version}.')
    if delay:
        predictions = get('predictions')
        if not predictions.empty:
            chosen = st.selectbox('Prediction model',predictions.model.unique())
            predictions = predictions[predictions.model==chosen].head(10000).copy()
            st.caption('Visual preview capped at 10,000 prediction rows; supply precomputed metrics for full evaluations.')
            chart(predictions,kind='scatter',x='actual_delay',y='predicted_delay',title='Actual versus predicted delay')
            predictions['residual'] = predictions.predicted_delay-predictions.actual_delay
            chart(predictions,kind='histogram',x='residual',title='Residual: predicted − actual (minutes)')
        else: absent('Supply predictions.csv for actual-versus-predicted and residual plots.')
    else:
        for kind2,title in [('bands','Passenger-band distribution'),('confusion','Confusion matrix'),('distance','Band-error distance distribution')]:
            details = get(kind2)
            if details.empty: absent(f'Supply {kind2}.csv for {title.lower()}.')
            elif kind2=='confusion':
                import plotly.express as px
                chosen = st.selectbox('Confusion-matrix model',details.model.unique())
                mat=details[details.model==chosen].pivot_table(index='actual_band',columns='predicted_band',values='count',aggfunc='sum')
                st.plotly_chart(px.imshow(mat,labels={'x':'Predicted band','y':'Actual band'},title=title),use_container_width=True)
            else: chart(details,x='band' if kind2=='bands' else 'band_distance',y='count',title=title)
        st.warning('Accuracy alone can be misleading with imbalanced multiclass data. Macro F1 gives equal weight to each class; compare both metrics and inspect band-distance errors.')
    notes('Predictors: mode (delay only), route, stop, direction, stop sequence, scheduled hour and minute; day of week for delay, missing-time indicator for occupancy. Actual arrivals, observed occupancy and post-event information must not enter predictors. Split strategy, test period, preprocessing and leakage controls must be supplied with future results. Existing V1 results do not establish performance on V3 or V4.')

elif page == PAGES[5]:
    data = get('benchmarks')
    if data.empty and mode == 'demo': data = demo('benchmarks',version)
    if not data.empty: data = data[data['mode']==selected_transport]
    if data.empty: absent('No confirmed storage/query benchmarks supplied. Add benchmarks.csv including environment and repetitions.')
    else:
        if data.synthetic.any(): st.warning(DEMO_LABEL)
        cols=st.columns(3)
        for col,key in zip(cols,['mode','category','format']):
            selected=col.selectbox(key.title(),['All']+sorted(data[key].unique()))
            if selected!='All': data=data[data[key]==selected]
        summary=data.groupby(['dataset_version','mode','category','format','workload','records','hardware','software','synthetic'],as_index=False).agg(repetitions=('seconds','count'),median_seconds=('seconds','median'),mean_seconds=('seconds','mean'),std_seconds=('seconds','std'),min_seconds=('seconds','min'),max_seconds=('seconds','max'),size_mb=('size_mb','max'))
        chart(summary,x='format',y='size_mb',color='format',barmode='group',title='Storage size (decimal MB)')
        chart(summary,x='workload',y='median_seconds',color='format',barmode='group',title='Median query execution time (seconds)')
        st.subheader('Runs and environment')
        table(data)
        st.dataframe(summary,hide_index=True,use_container_width=True)
        st.caption('Compression ratio = CSV bytes / Parquet bytes, only for identical dataset, mode and record scope. Summary rows remain separated by hardware/software and workload.')
        sizes=summary.groupby(['dataset_version','mode','records','hardware','software','format']).size_mb.max().unstack('format')
        if {'CSV','Parquet'}.issubset(sizes.columns):
            sizes['CSV / Parquet']=sizes.CSV / sizes.Parquet.replace(0,float('nan'))
            st.dataframe(sizes,use_container_width=True)
    notes('Record identical logical data in both formats. Report decimal MB (bytes / 1,000,000), hardware, library versions, query text/workload, cache policy and repetitions. Do not combine cold-cache and warm-cache runs. Demonstration figures describe no actual machine or research experiment.')

else:
    st.subheader('Research objectives')
    st.write('Integrate heterogeneous historical operational data, validate quality against GTFS, benchmark arrival-delay regression and light-rail occupancy classification, and evaluate analytical storage/query efficiency.')
    st.info(PIPELINE)
    st.subheader('Data sources and technology')
    st.write('BOAM: bus · FOAM: ferry · LOAM: light rail · ROAM: rail. Python, Pandas, DuckDB, PyArrow, Parquet, Streamlit and Plotly; Azure Blob Storage and GTFS are part of the wider research architecture. This application needs no cloud credentials.')
    st.subheader('Dataset registry')
    st.dataframe(pd.DataFrame([{'version':v,'label':version_label(v,m),'records':m['records'],'provenance':m['provenance']} for v,m in versions.items()]),hide_index=True)
    st.subheader('Quality principles and limitations')
    st.write('Retain provenance and scope; distinguish anomalies from confirmed errors; never sum overlapping checks. V1 and V4 are frozen benchmark releases; V3 remains provisional. V4 independent dataset QA is complete; its LOAM model results are validation only. Generalisation, class imbalance and temporal leakage require careful evaluation.')
    st.subheader('Contributors — configurable details')
    st.dataframe(pd.DataFrame(settings['contributors']),hide_index=True)
    st.subheader('Acknowledgements')
    st.write(settings['acknowledgements'])
