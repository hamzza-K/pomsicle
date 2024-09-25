import polars as pl
from inventory.inventory_payload import Payload
from banners import Banner

payload = Payload()

sheet = "InventoryTemplating"

filename = "../data/materials.xlsx"

def read_file(filename: str):
    df = pl.read_excel(filename, xlsx2csv_options={"skip_empty_lines": True})

    for record in df.iter_rows():
        Banner().info(f'Reading: {record}')
        pay = payload.fetch(record)
        # print('Payload', pay)
        
        
read_file(filename) 