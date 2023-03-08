from datetime import datetime, timezone

from gspread import Spreadsheet as Document, Worksheet
from dotenv import load_dotenv
import pytest

from app.spreadsheet_service import SpreadsheetService

load_dotenv()

CI_ENV = (os.getenv("CI", default="false") == "true")
CI_SKIP_MESSAGE = "taking a lighter touch to testing on the CI server, to reduce API usage and prevent rate limits"


def test_generate_timestamp():
    #dt = ss.generate_timestamp()
    dt = SpreadsheetService.generate_timestamp()
    assert isinstance(dt, datetime)
    assert dt.tzinfo == timezone.utc



def test_parse_timestamp():
    example_ts = "2023-03-08 19:59:16.471152+00:00"
    #dt = ss.parse_timestamp(example_ts)
    dt = SpreadsheetService.parse_timestamp(example_ts)
    assert isinstance(dt, datetime)
    assert dt.year == 2023
    assert dt.month == 3
    assert dt.day == 8
    assert dt.hour == 19
    assert dt.minute == 59
    assert dt.second == 16
    assert dt.tzinfo == timezone.utc


#
# READING DATA
#

@pytest.mark.skipif(CI_ENV, reason=CI_SKIP_MESSAGE)
def test_document(ss):
    assert isinstance(ss.doc, Document)


@pytest.mark.skipif(CI_ENV, reason=CI_SKIP_MESSAGE)
def test_get_sheet(ss):
    sheet = ss.get_sheet("products")
    assert isinstance(sheet, Worksheet)

#def test_get_records(ss):
#    sheet, products = ss.get_records("products")
#    assert isinstance(sheet, Worksheet)
#    assert isinstance(products, list)

@pytest.mark.skipif(CI_ENV, reason=CI_SKIP_MESSAGE)
def test_get_products(ss):
    sheet, products = ss.get_records("products")
    assert isinstance(sheet, Worksheet)
    assert len(products) == 3
    assert [p["name"] for p in products] == ["Strawberries", "Cup of Tea", "Textbook"]
    assert [p["id"] for p in products] == [1,2,3]

@pytest.mark.skipif(CI_ENV, reason=CI_SKIP_MESSAGE)
def test_get_orders(ss):
    sheet, orders = ss.get_records("orders")
    assert isinstance(sheet, Worksheet)
    assert not any(orders)


@pytest.mark.skipif(CI_ENV, reason=CI_SKIP_MESSAGE)
def test_destroy_all(ss):
    sheet, records = ss.get_records("products")
    assert len(records) == 3

    ss.destroy_all("products")

    sheet, records = ss.get_records("products")
    assert not any(records)


#
# WRITING DATA
#

@pytest.mark.skipif(CI_ENV, reason=CI_SKIP_MESSAGE)
def test_create_product(ss):

    sheet, products = ss.get_records("products")
    assert len(products) == 3

    new_product = {"name": "Mock Product", "price": 999.99, "description": "Testing 123...", "url": "https://picsum.photos/360/200"}
    ss.create_product(new_product)

    sheet, products = ss.get_records("products")
    assert len(products) == 4

    product = products[-1]
    assert product["id"] == 4
    assert product["name"] == "Mock Product"
    assert product["price"] == 999.99
    assert product["description"] == "Testing 123..."
    assert product["url"] == "https://picsum.photos/360/200"
    assert isinstance(product["created_at"], datetime)



@pytest.mark.skipif(CI_ENV, reason=CI_SKIP_MESSAGE)
def test_create_order(ss):
    sheet, orders = ss.get_records("orders")
    assert not any(orders)

    ss.create_order({"user_email": "example@test.com", "product_id": 3})

    sheet, orders = ss.get_records("orders")
    assert len(orders) == 1

    order = orders[0]
    assert order["id"] == 1
    assert order["product_id"] == 3
    assert order["user_email"] == "example@test.com"
    assert isinstance(order["created_at"], datetime)
