import os
import json
import configparser
import requests
from api.token import Token
from banners import Banner
from config import config
import logging


logger = logging.getLogger(__name__)
settings = config('pomsicle')

MACHINE_NAME = settings.get('MACHINE_NAME', None)

if not MACHINE_NAME:
    logger.critical("MACHINE_NAME is not configured. Exiting.")
    exit(1)

BASE_URL = f'http://{MACHINE_NAME}/poms-api/'

def login(username: str, password: str) -> Token | None:
    """
    Sends a request to the API to authenticate a user and get a new authentication token.
    """
    try:
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

            logger.info(f"✓ Successfully authorized '{username}' on '{MACHINE_NAME}'")
            return token
    except Exception as e:
        Banner().error(f"✗ Couldn't authorize '{username}' on '{MACHINE_NAME}'")
        logger.error(e)

