
import pytest

from app.spreadsheet_service import SpreadsheetService
from web_app import create_app


# an example sheet that is being used for testing purposes
TEST_DATABASE_DOCUMENT_ID="1TZCr9x6CZmlccSKgpOkAIE6dCfRmS_83tSlb_GyALsw"


@pytest.fixture(scope="module")
def ss():
    """spreadsheet service to use when testing"""
    ss = SpreadsheetService(document_id=TEST_DATABASE_DOCUMENT_ID)
    ss.seed_products()
    return ss


@pytest.fixture()
def test_client(ss):
    app = create_app(spreadsheet_service=ss)
    app.config.update({"TESTING": True})
    return app.test_client()
