import sys
import json
import requests


secrets = "config.json"

MACHINE_NAME = "win-bkblmqnn8d9"
TRANSLATOR_INSTANCE_ID = "stallergenes"
USERNAME = "administrator"
PASSWORD = "Karachi@123"
#with open(secrets, 'r', encoding="utf-8") as f:
#    env_vars = json.load(f)

#USERNAME     = env_vars.get('USERNAME')
#PASSWORD     = env_vars.get('PASSWORD')
#MACHINE_NAME = env_vars.get('MACHINE_NAME')

BASE_URL = f'http://{MACHINE_NAME}/poms-api/'
print(MACHINE_NAME, BASE_URL)
DEFAULT_MEDIA_TYPE = 'application/json'

class Token:
    """
    Class for managing authentication tokens.
    """
    def __init__(self, access_token, expires_in):
        self.access_token = access_token
        self.expires_in = expires_in

def login(username: str, password: str) -> None:
    """
    Sends a request to the API to authenticate a user and get a new authentication token.
    """
    base_url = BASE_URL
    token_url = base_url + 'token'

    # Set up the HTTP client and set the default media type to JSON
    http_client = requests.Session()
    http_client.headers.update({'Accept': 'application/json'})

    # Send a POST request to the token URL with the login parameters
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password
    }
    response = http_client.post(token_url, data=data)

    # Check if the request was successful and parse the response if it was
    if response.ok:
        token_data = json.loads(response.content)
        token = Token(token_data['access_token'], token_data['expires_in'])
        return token
    else:
        response.raise_for_status()

def interface(token, material_file):
    path = BASE_URL + 'v1/Interface/Transaction/Call'

    headers = {
        'Content-Type': DEFAULT_MEDIA_TYPE,
        'Authorization': f'Bearer {token}'
    }

    payload = {"InstanceID": TRANSLATOR_INSTANCE_ID, "TransactionID": "*", "TransactionValue": material_file}

    response = requests.post(path, json=payload, headers=headers)

    response = requests.post(path, json=payload, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        return response, response.text

if __name__ == '__main__':

    token = login(USERNAME, PASSWORD)

    material_file = sys.argv[1]
    
    with open(material_file, 'r') as f:
        material = f.read()
