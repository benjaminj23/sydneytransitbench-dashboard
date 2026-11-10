import streamlit as st
import plotly.express as px

PALETTE = {'Bus':'#2979df','Ferry':'#0baca0','Light rail':'#ed9635','Rail':'#805ad5'}
DEMO_LABEL = 'Illustrative demonstration data – not research findings.'

def style():
    st.markdown('''<style>
    .stApp {background:#f4f7fb;color:#15273c}
    [data-testid="stSidebar"] {background:#10253c}
    [data-testid="stSidebar"] * {color:#e4edf6}
    [data-testid="stMetric"] {background:white;border:1px solid #dfe7f0;border-radius:14px;padding:18px}
    h1,h2,h3 {letter-spacing:-.035em} .block-container {padding-top:2rem;max-width:1480px}
    </style>''', unsafe_allow_html=True)

def chart(frame, kind='bar', **kwargs):
    if frame.empty:
        st.info('No data supplied for this visualisation.')
        return
    if 'synthetic' in frame and frame.synthetic.any():
        st.warning(DEMO_LABEL)
    fig = getattr(px, kind)(frame, color_discrete_map=PALETTE, **kwargs)
    fig.update_layout(template='plotly_white',paper_bgcolor='rgba(0,0,0,0)',font=dict(family='Arial',color='#22354b'),margin=dict(t=45,l=15,r=15,b=20),legend_title_text='')
    st.plotly_chart(fig, use_container_width=True)

def table(frame):
    query = st.text_input('Search this table', key='search_' + str(tuple(frame.columns)))
    if query and not frame.empty:
        frame = frame[frame.astype(str).apply(lambda s:s.str.contains(query,case=False,regex=False)).any(axis=1)]
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.download_button('Download displayed CSV', frame.to_csv(index=False), 'displayed_results.csv', key='download_' + str(tuple(frame.columns)))
