
import pytest
import os
from dotenv import load_dotenv

from app.spreadsheet_service import SpreadsheetService
from web_app import create_app


load_dotenv()

# an example sheet that is being used for testing purposes:
GOOGLE_SHEETS_TEST_DOCUMENT_ID= os.getenv("GOOGLE_SHEETS_TEST_DOCUMENT_ID", default="1TZCr9x6CZmlccSKgpOkAIE6dCfRmS_83tSlb_GyALsw")


@pytest.fixture()
def ss():
    """spreadsheet service to use when testing"""
    ss = SpreadsheetService(document_id=GOOGLE_SHEETS_TEST_DOCUMENT_ID)

    # setup / remove any records that may exist:
    ss.destroy_all("products")
    ss.destroy_all("orders")

    # seed default products:
    ss.seed_products()

    yield ss

    # clean up:
    ss.destroy_all("products")
    ss.destroy_all("orders")



@pytest.fixture()
def test_client(ss):
    app = create_app(spreadsheet_service=ss)
    app.config.update({"TESTING": True})
    return app.test_client()
