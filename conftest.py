
import pytest

#from app.spreadsheet_service import SpreadsheetService
from web_app import create_app

# see: https://flask.palletsprojects.com/en/2.1.x/testing/

#@pytest.fixture(scope="module")
#def test_spreadsheet_service():
#    return SpreadsheetService()

@pytest.fixture()
def test_client():
    app = create_app()
    app.config.update({"TESTING": True})
    return app.test_client()
