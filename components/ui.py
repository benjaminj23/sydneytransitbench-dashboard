import streamlit as st
import plotly.express as px

PALETTE = {'Bus':'#2979df','Ferry':'#0baca0','Light rail':'#ed9635','Rail':'#805ad5'}
DEMO_LABEL = 'Illustrative demonstration data – not research findings.'

def style():
    st.markdown('''<style>
    .stApp {background:#f4f7fb;color:#15273c}
    [data-testid="stSidebar"] {background:#10253c}
    [data-testid="stSidebar"] * {color:#e4edf6}
    [data-testid="stSidebar"] [data-baseweb="select"] * {color:#15273c}
    [data-testid="stSidebar"] [data-testid="stAlert"] * {color:#15273c}
    [data-testid="stSidebar"] [role="combobox"], [data-testid="stSidebar"] [role="combobox"] * {color:#15273c!important}
    [data-testid="stMetric"] {background:white;border:1px solid #dfe7f0;border-radius:14px;padding:18px}
    h1,h2,h3 {letter-spacing:-.035em} .block-container {padding-top:4rem;max-width:1480px}
    .eyebrow{font-size:11px;font-weight:700;letter-spacing:.17em;color:#87a2c0}
    .mode-label{color:#526b85;margin:12px 0}
    .mode-hero{display:flex;align-items:center;justify-content:space-between;overflow:hidden;background:#10243b;border-radius:24px;padding:32px 40px;margin:18px 0 28px;min-height:310px;box-shadow:0 15px 40px #10243b15;border:1px solid #264360}
    .hero-copy{width:50%;position:relative;z-index:1}.hero-copy h1{font-size:48px;line-height:1.04;color:#f4f8fd!important;max-width:490px;margin:20px 0 15px;padding:0;font-weight:750}
    .hero-copy p{color:#a9bed3;font-size:16px;max-width:370px}.hero-tags{display:flex;gap:9px;margin-top:24px;flex-wrap:wrap}.hero-tags span{font-size:11px;color:#d9e7f4;border:1px solid #ffffff30;padding:6px 12px;border-radius:20px}
    .hero-tags span:first-child{border-color:var(--accent);color:white}.hero-art{width:49%;color:var(--accent);text-align:center}.hero-art svg{width:100%;overflow:visible}.art-caption{font-size:9px;letter-spacing:.18em;color:#7894b1}
    .vehicle{animation:arrive .7s cubic-bezier(.2,.8,.2,1) both}.ferry{animation:arrive .7s ease-out both,buoy 4s .7s ease-in-out infinite}
    @keyframes arrive{from{transform:translateX(90px);opacity:0}to{transform:translateX(0);opacity:1}}@keyframes buoy{50%{transform:translateY(-4px)}}
    @media(prefers-reduced-motion:reduce){.vehicle,.ferry{animation:none}}
    @media(max-width:800px){.mode-hero{padding:24px;min-height:240px}.hero-copy h1{font-size:30px}.hero-copy{width:55%}.hero-art{width:45%}.hero-copy p{font-size:13px}}
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
