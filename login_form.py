from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, quote_plus
from urllib.parse import urlparse, parse_qs
import requests
import json
import xml.etree.ElementTree as ET
import os
import logging
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from banners import Banner
import uuid

# --- Configuration ---
username = "administrator"
password = "Karachi@123"
login_host = "http://win-bkblmqnn8d9"
login_path = "/poms/DesktopDefault.aspx"
return_url = quote_plus("/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx")

login_url = f"{login_host}{login_path}?ReturnUrl={return_url}"
webmethod_url = "http://win-bkblmqnn8d9/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx/InitiateWorkSheet"

# --- Start session ---
session = requests.Session()
session.verify = False

# --- Step 1: Load login page and extract hidden fields ---
resp = session.get(login_url)
soup = BeautifulSoup(resp.text, "html.parser")
form = soup.find("form", id="loginForm")

login_data = {}
for input_tag in form.find_all("input"):
    name = input_tag.get("name")
    value = input_tag.get("value", "")
    if name:
        login_data[name] = value

# Add user credentials
login_data["txtUsername"] = username
login_data["txtPassword"] = password
login_data["__EVENTTARGET"] = "XbtnLogin"
login_data["__EVENTARGUMENT"] = ""

# Submit login
post_url = urljoin(login_url, form.get("action"))
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": login_url,
    "User-Agent": "Mozilla/5.0"
}

login_resp = session.post(post_url, data=login_data, headers=headers, allow_redirects=True)
if "login" in login_resp.url.lower() or "DesktopDefault.aspx" in login_resp.url:
    print("[❌] Login failed.")
    exit()
print("[✅] Login successful.")


logger = logging.getLogger(__name__)

class LoginManager:
    """
    Manages the upload and import of template XML files to POMSicle.
    """
    def __init__(self, settings: dict, username: str, password: str):
        """
        Initializes the PomsicleTemplateManager with configuration settings and credentials.

        Args:
            settings (dict): A dictionary containing POMSicle configuration details
                             (e.g., MACHINE_NAME, BASE_APP_URL).
            username (str): The username for POMSicle login.
            password (str): The password for POMSicle login.
        """
        self.settings = settings
        self.username = username
        self.password = password
        
        self.base_app_url = settings.get('BASE_APP_URL')
        self.import_url = settings.get('IMPORT_URL')
        self.file_upload_url = settings.get('FILE_UPLOAD_URL')
        self.login_host = settings.get('LOGIN_HOST')
        self.machine_name = settings.get('MACHINE_NAME')
        self.program_path = settings.get('PROGRAM_BASE_PATH')
        
        self.file_upload_url = self.login_host + '/' + self.base_app_url + '/' + self.file_upload_url
        self.import_url = self.login_host + '/' + self.base_app_url + '/' + self.import_url

        self.login_page_relative_path = "/POMS/DesktopDefault.aspx"
        self.espec_model_base_path = "/poms/apps/eSpecWebApplication/"
        self.espec_model_base_poms_path = "/poms/"

        if not all([self.username, self.password, self.machine_name, self.base_app_url,
                    self.import_url, self.file_upload_url, self.login_host]):
            logger.critical("Missing essential configuration variables in settings. Exiting.")
            raise ValueError("Missing essential configuration variables for PomsicleTemplateManager.")
        
        self.session = requests.Session()


    def _perform_login(self) -> bool:

        """
        Performs a browser-like login to the POMSicle system.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        logger.info("Attempting browser-like login via DesktopDefault.aspx...")

        initial_get_return_url_encoded = quote_plus(f"{self.espec_model_base_path}SpecificationManagement.aspx?AutoClose=1")
        initial_get_login_url = f"{self.login_host}{self.espec_model_base_poms_path}DesktopDefault.aspx?ReturnUrl={initial_get_return_url_encoded}"

        try:
            logger.debug(f"GETting login page for VIEWSTATEs: {initial_get_login_url}")
            login_page_response = self.session.get(initial_get_login_url, verify=False)
            login_page_response.raise_for_status()

            soup = BeautifulSoup(login_page_response.text, 'html.parser')

            login_form = soup.find('form', id='loginForm')
            if not login_form:
                logger.error("Could not find the login form with ID 'loginForm'.")
                return False

            login_data = {}
            for hidden_input in login_form.find_all('input', type='hidden'):
                name = hidden_input.get('name')
                value = hidden_input.get('value', '')
                if name:
                    login_data[name] = value

            login_data['txtUsername'] = self.username
            login_data['txtPassword'] = self.password
            login_data['__EVENTTARGET'] = 'XbtnLogin'
            login_data['__EVENTARGUMENT'] = ''

            form_action_url = login_form.get('action')
            if not form_action_url:
                logger.error("Login form does not have an 'action' attribute.")
                return False

            post_login_url = urljoin(initial_get_login_url, form_action_url)
            logger.debug(f"POSTing login data to: {post_login_url}")

            login_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": initial_get_login_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/533.36"
            }

            logger.debug(f"Login data being sent: {login_data}")
            login_response = self.session.post(post_login_url, data=login_data, headers=login_headers, allow_redirects=True, verify=False)
            login_response.raise_for_status()

            if self.login_page_relative_path in login_response.url or "POMSnet Login" in login_response.text:
                logger.error("Login failed. Check username, password, or server status.")
                logger.error(f"Login Response Status Code: {login_response.status_code}")
                logger.error(f"Login Response Content (start):\n{login_response.text[:1000]}...")
                return False
            else:
                logger.info(f"Browser-like login successful! Current URL after login: {login_response.url}")
                logger.debug(f"Session cookies after login: {self.session.cookies.get_dict()}")
                return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Browser-like login request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during browser-like login: {e}")
            return False


    def __call__(cls, *args, **kwargs):
        """
        Allows the class instance to be called like a function.
        """
        cls._perform_login()
        return cls.session