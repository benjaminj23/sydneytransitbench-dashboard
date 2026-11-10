"""Code-native vehicle illustrations and mode-aware dashboard presentation."""
import streamlit as st

MODES = {
 'Bus': ('#2979df', 'BOAM', 'Street-level connections.', 'Every stop tells a story.'),
 'Ferry': ('#0baca0', 'FOAM', 'A different view of the network.', 'Across the harbour, through the data.'),
 'Light rail': ('#ed9635', 'LOAM', 'The city, connected.', 'Explore stop-level operations and occupancy research.'),
 'Rail': ('#805ad5', 'ROAM', 'The backbone of movement.', 'Follow the patterns behind Sydney’s rail operations.'),
}

def vehicle(mode: str) -> str:
    """Stylised illustrations, not models of specific Sydney fleet vehicles."""
    windows=''.join(f'<rect x="{x}" y="98" width="48" height="53" rx="8" fill="#10243d"/><path d="M{x+7} 106h22l-29 35v-21z" fill="#ffffff" opacity=".12"/>' for x in [132,192,252,312])
    if mode=='Ferry':
        return '''<g class="vehicle ferry"><path d="M83 179h405l-45 62H149z" fill="#eaf4fc"/><path d="M93 197h383l-11 17H108z" fill="currentColor"/><path d="M139 177l30-76h211l43 76" fill="currentColor"/><rect x="174" y="114" width="191" height="43" rx="5" fill="#10243d"/><path d="M204 114v43m42-43v43m42-43v43m42-43v43" stroke="#78ccce" stroke-width="5"/><path d="M217 100V72h94l22 28" fill="#eaf4fc"/><path d="M275 72V46m0 4h51l-12 17h-39" stroke="#b9e7e8" fill="currentColor" stroke-width="4"/><path d="M76 252q26-16 52 0t52 0t52 0t52 0t52 0t52 0t52 0t52 0" stroke="#8be5dd" fill="none" stroke-width="4" opacity=".7"/></g>'''
    if mode=='Bus':
        return f'''<g class="vehicle"><rect x="104" y="77" width="362" height="134" rx="25" fill="#eaf4fc"/><path d="M105 164h360v25a22 22 0 0 1-22 22H126a22 22 0 0 1-22-22z" fill="currentColor"/>{windows}<rect x="378" y="98" width="61" height="96" rx="7" fill="#10243d"/><path d="M409 100v91" stroke="#b4c2d3" stroke-width="3"/><rect x="125" y="82" width="111" height="10" rx="3" fill="#10243d"/><circle cx="170" cy="211" r="24" fill="#071627"/><circle cx="170" cy="211" r="11" fill="#a6bdd0"/><circle cx="397" cy="211" r="24" fill="#071627"/><circle cx="397" cy="211" r="11" fill="#a6bdd0"/><rect x="454" y="163" width="12" height="12" rx="3" fill="#ffedaa"/></g>'''
    extra='<path d="M225 77l30-30 35 30m-55-30h48" stroke="#b1c9d9" stroke-width="5" fill="none"/>' if mode=='Light rail' else '<rect x="113" y="73" width="321" height="13" rx="6" fill="currentColor"/>'
    return f'''<g class="vehicle">{extra}<path d="M111 88h302q45 0 53 53l11 64H95V112q0-24 16-24" fill="#eaf4fc"/><path d="M96 162h373l8 43H95z" fill="currentColor"/>{windows}<path d="M380 101h31q32 0 35 49h-66z" fill="#10243d"/><path d="M98 126h366" stroke="currentColor" stroke-width="5"/><circle cx="158" cy="211" r="17" fill="#071627"/><circle cx="400" cy="211" r="17" fill="#071627"/><path d="M79 236h420m-420 9h420" stroke="#7895b2" stroke-width="3" opacity=".5"/><path d="M380 170h48" stroke="#ffedaa" stroke-width="4"/></g>'''

def hero(selected: str, version: str, status: str):
    color,source,title,subtitle=MODES[selected]
    st.markdown(f'''<section class="mode-hero" style="--accent:{color}">
      <div class="hero-copy"><div class="eyebrow">SYDNEY / {source} / {selected.upper()}</div>
      <h1>{title}</h1><p>{subtitle}</p><div class="hero-tags"><span>{status}</span><span>Historical research</span></div></div>
      <div class="hero-art"><svg viewBox="0 0 560 290" aria-label="Stylised {selected} illustration" role="img">
      <defs><radialGradient id="halo"><stop stop-color="{color}" stop-opacity=".35"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>
      <ellipse cx="280" cy="143" rx="275" ry="145" fill="url(#halo)"/>
      <path d="M21 246h510M49 260h440" stroke="#6485a6" opacity=".2"/>
      {vehicle(selected)}</svg><span class="art-caption">STYLISED VEHICLE · NO LIVE TRACKING</span></div></section>''',unsafe_allow_html=True)

def mode_selector() -> str:
    st.markdown('<div class="eyebrow mode-label">CHOOSE YOUR NETWORK</div>',unsafe_allow_html=True)
    cols=st.columns(4)
    if 'transport_mode' not in st.session_state: st.session_state.transport_mode='Bus'
    for col,(name,(color,source,_,_)) in zip(cols,MODES.items()):
        with col:
            if st.button(f'{name}  /  {source}',key='mode_'+name,use_container_width=True,type='primary' if st.session_state.transport_mode==name else 'secondary'):
                st.session_state.transport_mode=name
                st.rerun()
    return st.session_state.transport_mode
