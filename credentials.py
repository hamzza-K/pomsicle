import os
import json
import configparser
import requests
from api.token import Token
from config import config

settings = config('pomsicle')

MACHINE_NAME = settings["MACHINE_NAME"]

BASE_URL = f'http://{MACHINE_NAME}/poms-api/'

def login(username: str, password: str) -> None:
    """
    Sends a request to the API to authenticate a user and get a new authentication token.
    """
    base_url = BASE_URL
    token_url = base_url + 'token'

    http_client = requests.Session()
    http_client.headers.update({'Accept': 'application/json'})

    data = {
        'grant_type': 'password',
        'username': username,
        'password': password
    }
    response = http_client.post(token_url, data=data)

    if response.ok:
        token_data = json.loads(response.content)
        token = Token(token_data['access_token'], token_data['expires_in'])
        print(f"Logged in as {username}")
        return token
    else:
        response.raise_for_status()

