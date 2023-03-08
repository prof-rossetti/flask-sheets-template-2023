from datetime import datetime, timezone

from gspread import Spreadsheet as Document, Worksheet

from app.spreadsheet_service import SpreadsheetService

def test_generate_timestamp(ss):
    # class method for timestamp generation
    assert isinstance(SpreadsheetService.generate_timestamp(), datetime)

    dt = ss.generate_timestamp()
    assert isinstance(dt, datetime)
    assert dt.tzinfo == datetime.timezone.utc



def test_parse_timestamp(ss):
    # class method for timestamp generation
    assert isinstance(SpreadsheetService.generate_timestamp(), datetime)

    example_ts = "2023-03-08 19:59:16.471152+00:00"
    dt = ss.parse_timestamp(example_ts)
    assert isinstance(dt, datetime)
    assert dt.year == 2023
    assert dt.month == 3
    assert dt.day == 8
    assert dt.hour == 19
    assert dt.minute == 59
    assert dt.second == 16
    assert dt.tzinfo == timezone.utc



def test_document(ss):
    assert isinstance(ss.doc, Document)


def test_get_sheet(ss):
    sheet = ss.get_sheet("products")
    assert isinstance(sheet, Worksheet)

def test_get_records(ss):
    sheet, products = ss.get_records("products")
    assert isinstance(sheet, Worksheet)
    assert isinstance(products, list)

def test_get_products(ss):
    sheet, products = ss.get_records("products")
    assert isinstance(sheet, Worksheet)
    assert len(products) == 3
    assert [p["name"] for p in products] == ["Strawberries", "Cup of Tea", "Textbook"]
    assert [p["id"] for p in products] == [1,2,3]

def test_get_orders(ss):
    sheet, orders = ss.get_records("orders")
    assert isinstance(sheet, Worksheet)
    assert not any(orders)


def test_destroy_all(ss):
    sheet, records = ss.get_records("products")
    assert len(records) == 3

    ss.destroy_all("products")

    sheet, records = ss.get_records("products")
    assert not any(records)



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



def test_create_order(ss):
    sheet, orders = ss.get_records("orders")
    assert not any(orders)

    ss.create_order({"user_email": "example@test.com", "product_id": 1})

    sheet, orders = ss.get_records("orders")
    assert len(orders) == 1

    order = orders[0]
    breakpoint()
    #assert isinstance(order["created_at"], datetime)




# service.create_order(user_email=current_user["email"], product_info=product_info)
