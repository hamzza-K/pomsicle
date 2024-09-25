import polars as pl
import time
from inventory.inventory_payload import Payload
from banners import Banner
from api.transaction import call

payload = Payload()

SHEET = "InventoryTemplating"


def read_file(token: str, filename: str):
    df = pl.read_excel(
        filename, sheet_name=SHEET, xlsx2csv_options={"skip_empty_lines": True}
    )

    for record in df.iter_rows():
        Banner().info(f"Reading: {record}")
        pay = payload.fetch(record)
        print("Payload", pay)
        time.sleep(1)
        print(call(token, pay))

