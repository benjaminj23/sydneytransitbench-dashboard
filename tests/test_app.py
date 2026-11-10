from streamlit.testing.v1 import AppTest
from services.data_loader import ROOT

def test_all_demo_pages():
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30).run()
    assert not app.exception
    for page in app.sidebar.radio[0].options:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page

def test_real_missing_v4():
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30).run()
    app.sidebar.selectbox[0].set_value('V4')
    app.sidebar.selectbox[1].set_value('real').run()
    for page in app.sidebar.radio[0].options:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page

def test_v1_models_and_explorer():
    app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30).run()
    app.sidebar.selectbox[0].set_value('V1')
    for page in ['Arrival Delay Prediction','Occupancy Prediction']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception
        assert len(app.dataframe)>0
    app.sidebar.radio[0].set_value('Transport Network Explorer').run()
    app.button[0].click().run()
    assert not app.exception
    assert len(app.dataframe)>0
