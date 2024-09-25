import requests
from configparser import SectionProxy

settings = SectionProxy

MACHINE_NAME = settings["MACHINE_NAME"]
TRANSLATOR_INSTANCE_ID = settings["TRANSLATOR_INSTANCE_ID"]
BASE_URL = f"http://{MACHINE_NAME}/poms-api/"
DEFAULT_MEDIA_TYPE = "application/json"


def call(token: str, material_file: str):
    path = BASE_URL + "v1/Interface/Transaction/Call"

    headers = {"Content-Type": DEFAULT_MEDIA_TYPE, "Authorization": f"Bearer {token}"}

    payload = {
        "InstanceID": TRANSLATOR_INSTANCE_ID,
        "TransactionID": "*",
        "TransactionValue": material_file,
    }

    response = requests.post(path, json=payload, headers=headers, timeout=10)

    if response.status_code == 200:
        return response.text
    else:
        return response, response.text
