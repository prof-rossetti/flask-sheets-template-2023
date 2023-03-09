
# adapted from:
# ... https://developers.google.com/sheets/api/guides/authorizing
# ... https://gspread.readthedocs.io/en/latest/oauth2.html
# ... https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
# ... https://github.com/s2t2/birthday-wishes-py/blob/master/app/sheets.py
# ... https://raw.githubusercontent.com/prof-rossetti/flask-sheets-template-2020/master/web_app/spreadsheet_service.py

import os
from datetime import datetime, timezone
from pprint import pprint

from dotenv import load_dotenv
import gspread
from gspread.exceptions import SpreadsheetNotFound


load_dotenv()

DEFAULT_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "google-credentials.json")
GOOGLE_CREDENTIALS_FILEPATH = os.getenv("GOOGLE_CREDENTIALS_FILEPATH", default=DEFAULT_FILEPATH)

GOOGLE_SHEETS_DOCUMENT_ID = os.getenv("GOOGLE_SHEETS_DOCUMENT_ID", default="OOPS Please get the spreadsheet identifier from its URL, and set the 'GOOGLE_SHEETS_DOCUMENT_ID' environment variable accordingly...")


class SpreadsheetService:
    # TODO: consider implementing a locking mechanism on sheet writes, to prevent overwriting (if it becomes an issue)
    # ... however we know that if we want a more serious database solution, we would choose SQL database (and this app is just a small scale demo)

    def __init__(self, credentials_filepath=GOOGLE_CREDENTIALS_FILEPATH, document_id=GOOGLE_SHEETS_DOCUMENT_ID):
        print("INITIALIZING NEW SPREADSHEET SERVICE...")

        #self.credentials = credentials or ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILEPATH, AUTH_SCOPE)
        #self.credentials = ServiceAccountCredentials._from_parsed_json_keyfile(json.loads(GOOGLE_API_CREDENTIALS), AUTH_SCOPE)
        #self.client = gspread.authorize(self.credentials) #> <class 'gspread.client.Client'>
        self.client = gspread.service_account(filename=credentials_filepath)

        self.document_id = document_id

        # TODO: consider storing and caching the latest version of each sheet, given the small number of sheets
        # ... showing preference for speed over brevity
        #self.products_sheet = None
        #self.orders_sheet = None

    @staticmethod
    def generate_timestamp():
        return datetime.now(tz=timezone.utc)

    @staticmethod
    def parse_timestamp(ts:str):
        """
            ts (str) : a timestamp string like '2023-03-08 19:59:16.471152+00:00'
        """
        date_format = "%Y-%m-%d %H:%M:%S.%f%z"
        return datetime.strptime(ts, date_format)

    # READING DATA
    # ... TODO: consider passing the sheet or the sheet name, and getting the sheet only if necessary

    @property
    def doc(self):
        """note: this will make an API call each time, to get the new data"""
        return self.client.open_by_key(self.document_id) #> <class 'gspread.models.Spreadsheet'>

    def get_sheet(self, sheet_name):
        return self.doc.worksheet(sheet_name)

    def get_records(self, sheet_name):
        """Gets all records from a sheet,
            converts datetime columns back to Python datetime objects
        """
        #print(f"GETTING RECORDS FROM SHEET: '{sheet_name}'")
        sheet = self.get_sheet(sheet_name) #> <class 'gspread.models.Worksheet'>
        records = sheet.get_all_records() #> <class 'list'>
        for record in records:
            if record.get("created_at"):
                record["created_at"] = self.parse_timestamp(record["created_at"])
        return sheet, records

    def destroy_all(self, sheet_name):
        """Removes all records from a given sheet, except the header row."""
        sheet, records = self.get_records(sheet_name)
        # start on the second row, and delete one more than the number of records,
        # ... to account for the header row
        sheet.delete_rows(start_index=2, end_index=len(records)+1)


    #def insert_records(self, sheet):
    #    pass







    #def get_record_by_id(self, sheet_name, record_id):
    #    return True # TODO



    #def insert_record(self, sheet_name, record):
    #    sheet = self.get_sheet(sheet_name)
    #    response = sheet.insert_row(record)
    #    print("INSERT RECORD RESPONSE")
    #    print(response)
    #    return response


    #def insert_records(self, sheet_name, records):
    #    sheet = self.get_sheet(sheet_name)
    #    response = sheet.insert_rows(records)
    #    print("INSERT RECORDS RESPONSE")
    #    print(response)
    #    return response



    # PRODUCT SPECIFIC STUFF



    #def create_product(self, product_attributes):
    #    print("NEW PRODUCT ATTRIBUTES:", product_attributes)
#
    #    sheet, products = self.get_records("products")
    #    print(f"DETECTED {len(products)} EXISTING PRODUCTS")
    #    next_row_number = len(products) + 2 # number of records, plus a header row, plus one
#
    #    if any(products):
    #        product_ids = [int(p["id"]) for p in products]
    #        next_id = max(product_ids) + 1
    #    else:
    #        next_id = 1
#
    #    new_product = {
    #        "id": next_id,
    #        "name": product_attributes["name"],
    #        "department": product_attributes["department"],
    #        "price": float(product_attributes["price"]),
    #        "availability_date": product_attributes["availability_date"],
    #        "img_url": product_attributes["img_url"]
    #    }
    #    next_row = list(new_product.values()) #> [13, 'Product CLI', 'snacks', 4.99, '2019-01-01']
    #    response = sheet.insert_row(next_row, next_row_number)
    #    return response



    #def get_product(self, product_id):
    #    """
    #    Will return None if product identifier not found in the list.
    #    Otherwise will return the product as a dictionary.
    #    """
    #    sheet, products = self.get_records("products")
    #    matching_products = [p for p in products if str(p["id"]) == str(product_id)]
    #    try:
    #        return matching_products[0]
    #    except IndexError:
    #        return None


    def get_products(self):
        _, products = self.get_records("products")
        return products

    def get_orders(self):
        _, orders = self.get_records("orders")
        return records

    def get_user_orders(self, user_email):
        _, orders = self.get_records("orders")
        return [order for order in orders if order["user_email"] == user_email]


    # WRITING DATA

    def seed_products(self):
        sheet, products = self.get_records("products")
        if not any(products):
            DEFAULT_PRODUCTS = [
                {'id': 1, 'name': 'Strawberries', 'description': 'Juicy organic strawberries.', 'price': 4.99, 'url': 'https://picsum.photos/id/1080/360/200'},
                {'id': 2, 'name': 'Cup of Tea', 'description': 'An individually-prepared tea or coffee of choice.', 'price': 3.49, 'url': 'https://picsum.photos/id/225/360/200'},
                {'id': 3, 'name': 'Textbook', 'description': 'It has all the answers.', 'price': 129.99, 'url': 'https://picsum.photos/id/24/360/200'}
            ]
            self.create_products(DEFAULT_PRODUCTS)

    def create_products(self, new_products:list):
        sheet, products = self.get_records("products")
        next_row_number = len(products) + 2 # plus headers plus one

        if any(products):
            product_ids = [p["id"] for p in products]
            next_id = max(product_ids) + 1
        else:
            next_id = 1

        new_rows = []
        for new_product in new_products:
            new_product["id"] = next_id
            new_product["created_at"] = self.generate_timestamp()
            new_row = Product(new_product).to_row
            new_rows.append(new_row)

            next_id += 1

        sheet.insert_rows(new_rows, row=next_row_number)

    def create_product(self, new_product:dict):
        self.create_products([new_product])


    def create_orders(self, new_orders:list):
        sheet, records = self.get_records("orders")
        next_row_number = len(records) + 2 # plus headers plus one

        # auto-increment integer identifier
        if any(records):
            existing_ids = [r["id"] for r in records]
            next_id = max(existing_ids) + 1
        else:
            next_id = 1

        new_rows = []
        for new_order in new_orders:
            new_order["id"] = next_id
            new_order["created_at"] = self.generate_timestamp()
            new_row = Order(new_order).to_row
            new_rows.append(new_row)

            next_id += 1

        sheet.insert_rows(new_rows, row=next_row_number)

    def create_order(self, new_order:dict):
        self.create_orders([new_order])




    #def create_order(self, new_order):
    #    new_order["created_at"] = self.generate_timestamp()
#
    #    sheet, orders = self.get_records("orders")
    #    next_row_number = len(orders) + 2 # plus headers plus one
#
    #    new_row = Order(new_order).to_row





# FIXED SCHEMA / DECORATORS
# ... to make sure when writing to sheet the values are in the proper order

class Product:
    def __init__(self, attrs):
        self.id = attrs.get("id")
        self.name = attrs.get("name")
        self.description = attrs.get("description")
        self.price = attrs.get("price")
        self.url = attrs.get("url")
        self.created_at = attrs.get("created_at")

    @property
    def to_row(self):
        return [self.id, self.name, self.description, self.price, self.url, str(self.created_at)]


class Order:
    def __init__(self, attrs):
        self.id = attrs.get("id")
        self.user_email = attrs.get("user_email")
        self.product_id = attrs.get("product_id")
        self.product_name = attrs.get("product_name")
        self.product_price = attrs.get("product_price")
        self.created_at = attrs.get("created_at")


    @property
    def to_row(self):
        return [self.id, self.user_email, self.product_id, self.product_name, self.product_price, str(self.created_at)]


if __name__ == "__main__":

    ss = SpreadsheetService()

    ss.seed_products()

    sheet, records = ss.get_records("products")

    for record in records:
        print("-----")
        pprint(record)
