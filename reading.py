import polars as pl
from banners import Banner
from read_file import Payload
from transact_api import login, USERNAME, PASSWORD, interface

ban = Banner()

token = login(USERNAME, PASSWORD)
payload = Payload('json')
sheet = "MaterialTemplating"


def read_file(filename: str):
    df = pl.read_excel(filename, xlsx2csv_options={"skip_empty_lines": True})

    for record in df.iter_rows():
        print("Reading:", record)
        print("===========================")
        pay = payload.fetch(record)
        print('Payload', pay)
        res = interface(token.access_token, pay)
        print(res)
        """if res.status_code == 400:
            Banner("*").error(res.text['Message'])
        if res.status_code == 200:
            Banner("+").success(res.text['Message'])"""
        
        
