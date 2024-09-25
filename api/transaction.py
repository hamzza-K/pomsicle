import os
import requests
import configparser

config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), '../config/config.cfg')
config.read(config_file)
settings = config['pomsicle']

MACHINE_NAME = settings["MACHINE_NAME"]
BASE_URL = f'http://{MACHINE_NAME}/poms-api/'
TRANSLATOR_INSTANCE_ID = settings["TRANSLATOR_INSTANCE_ID"]
DEFAULT_MEDIA_TYPE = "application/xml"


def call(token: str, material_file: str):
    path = BASE_URL + "v1/Interface/Transaction/Call"

    headers = {"Content-Type": DEFAULT_MEDIA_TYPE, "Authorization": f"Bearer {token}"}

    payload = {
        "InstanceID": TRANSLATOR_INSTANCE_ID,
        "TransactionID": "*",
        "TransactionValue": material_file,
    }

    response = requests.post(path, data=payload, headers=headers, timeout=10)

    if response.status_code == 200:
        return response.text
    else:
        return response, response.text
