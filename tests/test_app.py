from streamlit.testing.v1 import AppTest
from services.data_loader import ROOT

def test_all_demo_pages():
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30).run()
    assert not app.exception
    for page in app.sidebar.radio[0].options:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page
        if page=='Research':
            for topic in next(x for x in app.selectbox if x.label=='Research topic').options:
                next(x for x in app.selectbox if x.label=='Research topic').set_value(topic).run()
                assert not app.exception, topic

def test_real_missing_v4():
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30).run()
    app.sidebar.selectbox[0].set_value('V4')
    app.sidebar.selectbox[1].set_value('real').run()
    for page in app.sidebar.radio[0].options:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page
        if page=='Research':
            for topic in next(x for x in app.selectbox if x.label=='Research topic').options:
                next(x for x in app.selectbox if x.label=='Research topic').set_value(topic).run()
                assert not app.exception, topic

def test_v1_models_and_explorer():
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30).run()
    app.sidebar.selectbox[0].set_value('V1')
    app.sidebar.radio[0].set_value('Research').run()
    for page in ['Arrival Delay Prediction','Occupancy Prediction']:
        next(x for x in app.selectbox if x.label=='Research topic').set_value(page).run()
        assert not app.exception
        assert len(app.dataframe)>0
    app.sidebar.radio[0].set_value('Explore').run()
    app.button[-1].click().run()
    assert not app.exception
    assert len(app.dataframe)>0


def test_vehicle_selection_filters_dashboard():
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30).run()
    for selected in ['Ferry','Light rail','Rail','Bus']:
        app.button(key='mode_'+selected).click().run()
        assert not app.exception
        assert app.session_state['transport_mode']==selected
        assert any(selected in str(item.value) for item in app.markdown)
