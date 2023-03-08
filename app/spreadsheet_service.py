
# adapted from:
# ... https://developers.google.com/sheets/api/guides/authorizing
# ... https://gspread.readthedocs.io/en/latest/oauth2.html
# ... https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
# ... https://github.com/s2t2/birthday-wishes-py/blob/master/app/sheets.py
# ... https://raw.githubusercontent.com/prof-rossetti/flask-sheets-template-2020/master/web_app/spreadsheet_service.py

import json
import os
import random
from pprint import pprint

from dotenv import load_dotenv
import gspread
from gspread.exceptions import SpreadsheetNotFound
#from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

#GOOGLE_API_CREDENTIALS = os.getenv("GOOGLE_API_CREDENTIALS")
DEFAULT_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "google-credentials.json")
GOOGLE_CREDENTIALS_FILEPATH = os.getenv("GOOGLE_CREDENTIALS_FILEPATH", default=DEFAULT_FILEPATH)

#AUTH_SCOPE = [
#    "https://www.googleapis.com/auth/spreadsheets", #> Allows read/write access to the user's sheets and their properties.
#    "https://www.googleapis.com/auth/drive.file" #> Per-file access to files created or opened by the app.
#]

GOOGLE_SHEETS_DOCUMENT_ID = os.getenv("GOOGLE_SHEETS_DOCUMENT_ID", default="OOPS Please get the spreadsheet identifier from its URL, and set the 'GOOGLE_SHEETS_DOCUMENT_ID' environment variable accordingly...")


class SpreadsheetService():
    def __init__(self, credentials_filepath=GOOGLE_CREDENTIALS_FILEPATH, document_id=GOOGLE_SHEETS_DOCUMENT_ID):
        print("INITIALIZING NEW SPREADSHEET SERVICE...")

        #self.credentials = credentials or ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILEPATH, AUTH_SCOPE)
        #self.credentials = ServiceAccountCredentials._from_parsed_json_keyfile(json.loads(GOOGLE_API_CREDENTIALS), AUTH_SCOPE)
        #self.client = gspread.authorize(self.credentials) #> <class 'gspread.client.Client'>
        self.client = gspread.service_account(filename=credentials_filepath)

        self.document_id = document_id


    @property
    def doc(self):
        """note: this will make an API call each time, to get the new data"""
        return self.client.open_by_key(self.document_id) #> <class 'gspread.models.Spreadsheet'>


    def get_sheet(self, sheet_name):
        return self.doc.worksheet(sheet_name)


    def get_records(self, sheet_name):
        print(f"GETTING RECORDS FROM SHEET: '{sheet_name}'")
        sheet = self.get_sheet(sheet_name) #> <class 'gspread.models.Worksheet'>
        records = sheet.get_all_records() #> <class 'list'>
        return sheet, records


    def get_record_by_id(self, sheet_name, record_id):
        return True # TODO



    def insert_record(self, sheet_name, record):
        sheet = self.get_sheet(sheet_name)
        response = sheet.insert_row(record)
        print("INSERT RECORD RESPONSE")
        print(response)
        return response


    def insert_records(self, sheet_name, records):
        sheet = self.get_sheet(sheet_name)
        response = sheet.insert_rows(records)
        print("INSERT RECORDS RESPONSE")
        print(response)
        return response



    # PRODUCT SPECIFIC STUFF

    def seed_products(self, default_products=None):
        sheet, products = self.get_records("products")
        if not any(products):
            default_products = default_products or [
                {'id': 1, 'name': 'Strawberries', 'description': 'Juicy organic strawberries.', 'price': 4.99, 'url': 'https://picsum.photos/id/1080/360/200'},
                {'id': 2, 'name': 'Cup of Tea', 'description': 'An individually-prepared tea or coffee of choice.', 'price': 3.49, 'url': 'https://picsum.photos/id/225/360/200'},
                {'id': 3, 'name': 'Textbook', 'description': 'It has all the answers.', 'price': 129.99, 'url': 'https://picsum.photos/id/24/360/200'}
            ]
            print("SEEDING DEFAULT PRODUCTS...")
            # sheet interface likes list of lists format, make sure all values are in the right order!
            new_rows = [Product(attrs).to_row for attrs in DEFAULT_PRODUCTS]
            sheet.insert_rows(new_rows, row=2) # start on second row, below headers



    def create_product(self, product_attributes):
        print("NEW PRODUCT ATTRIBUTES:", product_attributes)

        sheet, products = self.get_records("products")
        print(f"DETECTED {len(products)} EXISTING PRODUCTS")
        next_row_number = len(products) + 2 # number of records, plus a header row, plus one

        if any(products):
            product_ids = [int(p["id"]) for p in products]
            next_id = max(product_ids) + 1
        else:
            next_id = 1

        new_product = {
            "id": next_id,
            "name": product_attributes["name"],
            "department": product_attributes["department"],
            "price": float(product_attributes["price"]),
            "availability_date": product_attributes["availability_date"],
            "img_url": product_attributes["img_url"]
        }
        next_row = list(new_product.values()) #> [13, 'Product CLI', 'snacks', 4.99, '2019-01-01']
        response = sheet.insert_row(next_row, next_row_number)
        return response

    def get_product(self, product_id):
        """
        Will return None if product identifier not found in the list.
        Otherwise will return the product as a dictionary.
        """
        sheet, products = self.get_records("products")
        matching_products = [p for p in products if str(p["id"]) == str(product_id)]
        try:
            return matching_products[0]
        except IndexError:
            return None


# FIXED SCHEMA:

class Product:
    def __init__(self, attrs):
        self.id = attrs.get("id")
        self.name = attrs.get("name")
        self.description = attrs.get("description")
        self.price = attrs.get("price")
        self.url = attrs.get("url")

    @property
    def to_row(self):
        return [self.id, self.name, self.description, self.price, self.url]


if __name__ == "__main__":

    ss = SpreadsheetService()

    ss.seed_products()

    sheet, records = ss.get_records("products")

    for record in records:
        print("-----")
        pprint(record)
