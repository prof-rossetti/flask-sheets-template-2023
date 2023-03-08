from gspread import Spreadsheet as Document, Worksheet
# service.fetch_products()

def test_document(ss):
    assert isinstance(ss.doc, Document)


def test_get_sheet(ss):
    sheet = ss.get_sheet("products")
    assert isinstance(sheet, Worksheet)

def test_get_records(ss):
    sheet, products = ss.get_records("products")
    assert isinstance(sheet, Worksheet)
    assert len(products) == 3

# service.fetch_user_orders(current_user["email"])



# service.create_order(user_email=current_user["email"], product_info=product_info)
