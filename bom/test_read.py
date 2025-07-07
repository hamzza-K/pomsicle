import polars as pl
from bom_payload import Payload

payload = Payload()

sheet = "BOMTemplating"

filename = "../data/materials.xlsx"

df = pl.read_excel(filename, engine="xlsx2csv", engine_options={"skip_empty_lines": True}, sheet_name=sheet)

payload.fetch(df)
