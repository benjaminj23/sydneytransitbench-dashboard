import streamlit as st
import plotly.express as px
px.defaults.template = 'plotly_dark'

PALETTE = {'Bus':'#2979df','Ferry':'#0baca0','Light rail':'#ed9635','Rail':'#805ad5'}
DEMO_LABEL = 'Illustrative demonstration data – not research findings.'

def style():
    st.markdown('''<style>
    .stApp {background:#090f1b;color:#e6edf7;color-scheme:dark}
    [data-testid="stHeader"] {background:#090f1bf0}
    [data-testid="stSidebar"] {background:#0d1727;border-right:1px solid #22334a}
    [data-testid="stMetric"] {background:#111e30;border:1px solid #27384f;border-radius:14px;padding:18px}
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {color:#e6edf7}
    [data-testid="stCaptionContainer"] {color:#99acc4}
    [data-testid="stBaseButton-secondary"] {background:#142136;color:#dce8f5;border-color:#31445d}
    [data-testid="stBaseButton-secondary"]:hover {border-color:#18b7b0;background:#1b3045}
    [data-testid="stAlert"] {border:1px solid #ffffff12;border-radius:12px}
    [data-testid="stExpander"] {background:#101c2d;border-color:#27384f;border-radius:12px}
    h1,h2,h3 {letter-spacing:-.035em} .block-container {padding-top:4rem;max-width:1480px}
    .eyebrow{font-size:11px;font-weight:700;letter-spacing:.17em;color:#87a2c0}
    .mode-label{color:#9aafc9;margin:12px 0}
    .mode-hero{display:flex;align-items:center;justify-content:space-between;overflow:hidden;background:#10243b;border-radius:24px;padding:32px 40px;margin:18px 0 28px;min-height:310px;box-shadow:0 15px 40px #10243b15;border:1px solid #264360}
    .hero-copy{width:50%;position:relative;z-index:1}.hero-copy h1{font-size:48px;line-height:1.04;color:#f4f8fd!important;max-width:490px;margin:20px 0 15px;padding:0;font-weight:750}
    .hero-copy p{color:#a9bed3;font-size:16px;max-width:370px}.hero-tags{display:flex;gap:9px;margin-top:24px;flex-wrap:wrap}.hero-tags span{font-size:11px;color:#d9e7f4;border:1px solid #ffffff30;padding:6px 12px;border-radius:20px}
    .hero-tags span:first-child{border-color:var(--accent);color:white}.hero-art{width:49%;color:var(--accent);text-align:center}.hero-art svg{width:100%;overflow:visible}.art-caption{font-size:9px;letter-spacing:.18em;color:#7894b1}
    .photo-frame{position:relative;overflow:hidden;border-radius:16px;border:1px solid #ffffff20;box-shadow:0 15px 40px #0005;animation:arrive .65s ease-out both}
    .transport-photo{display:block;width:100%;height:300px;object-fit:cover;transition:transform .6s ease;object-position:center 58%}
    .photo-frame:hover .transport-photo{transform:scale(1.04)}
    .photo-label{position:absolute;bottom:0;left:0;right:0;padding:35px 15px 14px;background:linear-gradient(transparent,#07111ee8);color:#fff;font-size:10px;text-align:left;letter-spacing:.12em}
    @media(max-width:800px){.transport-photo{height:240px}}@media(max-width:550px){.mode-hero{flex-direction:column;gap:24px}.hero-copy,.hero-art{width:100%}.transport-photo{height:220px}}
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
    fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#111e30',font=dict(family='Arial',color='#c7d6e8'),margin=dict(t=45,l=15,r=15,b=20),legend_title_text='')
    fig.update_xaxes(gridcolor='#24344a',zerolinecolor='#31445d')
    fig.update_yaxes(gridcolor='#24344a',zerolinecolor='#31445d')
    st.plotly_chart(fig, use_container_width=True)

def table(frame):
    query = st.text_input('Search this table', key='search_' + str(tuple(frame.columns)))
    if query and not frame.empty:
        frame = frame[frame.astype(str).apply(lambda s:s.str.contains(query,case=False,regex=False)).any(axis=1)]
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.download_button('Download displayed CSV', frame.to_csv(index=False), 'displayed_results.csv', key='download_' + str(tuple(frame.columns)))
