import pytest
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.epw import EPW
import os

# Can import, but need to change the relative modules to global or else fails
#from ladybug.comfort.pmv import PMV()

class TestLadybugCase():
    """Simple test for ladybug modules to ensure recursive import modules works"""

    def test_ladybug_analysisperiod_init(self):
        test_analysis = AnalysisPeriod()
        assert test_analysis.st_month == pytest.approx(1.0, abs=1e-15)
        assert test_analysis.end_day == pytest.approx(31.0, abs=1e-15)
        assert test_analysis.st_hour == pytest.approx(0.0, abs=1e-15)
        assert test_analysis.end_hour == pytest.approx(23.0, abs=1e-15)

    def test_ladybug_epw(self):
        CURR_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
        test_file_path = os.path.join(CURR_DIRECTORY, "room//epws//USA_AK_Anchorage.Intl.AP.702730_TMY3.epw")
        test_epw = EPW(test_file_path)
        test_epw.import_data()

        assert test_epw.location.city == "Anchorage Intl Ap"
        assert test_epw.location.country == "USA"
        assert test_epw.location.latitude == 61.18
