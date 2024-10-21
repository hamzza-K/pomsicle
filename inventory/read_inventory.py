import os
import time
import polars as pl
import configparser
from inventory.inventory_payload import Payload
from api.transaction import call

payload = Payload()

config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), '../config/config.cfg')
config.read(config_file)
settings = config['pomsicle']
SHEET = settings['INVENTORY_SHEET']


def read_file(token: str, filename: str):
    df = pl.read_excel(
        filename, sheet_name=SHEET, xlsx2csv_options={"skip_empty_lines": True}
    )

    for record in df.iter_rows():
        print(record)
        pay = payload.fetch(record)
        time.sleep(2)
        call(token, pay)

