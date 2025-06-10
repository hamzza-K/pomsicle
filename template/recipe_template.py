import requests
import json
import xml.etree.ElementTree as ET
import os
import logging
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import uuid

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# --- Configuration ---
BASE_APP_URL = "http://win-bkblmqnn8d9/poms/apps/eSpecWebApplication/"
IMPORT_URL = f"{BASE_APP_URL}SpecificationManagement.aspx/ImportFiles"
FILE_UPLOAD_URL = f"{BASE_APP_URL}SpecFileHandler.ashx"

LOGIN_HOST = "http://win-bkblmqnn8d9"
LOGIN_PAGE_RELATIVE_PATH = "/POMS/DesktopDefault.aspx"

USERNAME = "administrator"
PASSWORD = "Karachi@123"

ESPEC_MODEL_BASE_PATH = "/poms/apps/eSpecWebApplication/"
ESPEC_MODEL_BASE_POMS_PATH = "/poms/"

# --- XML File Processing ---
xml_folder = "../data"
xml_file_name = "Template.xml"
xml_file_path = os.path.join(xml_folder, xml_file_name)

if not os.path.exists(xml_file_path):
    logger.error(f"XML file not found at '{xml_file_path}'. Please ensure the 'data' folder exists and contains the XML file.")
    exit()

obj_type = ""
level_id = ""
location_id = ""
file_size = os.path.getsize(xml_file_path)

try:
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    e_proc_object = root.find(".//eProcObject")

    if e_proc_object is None:
        logger.warning("Could not find 'eProcObject' element in the XML file. Using placeholder values.")
        obj_type = "ConfiguredObject"
        level_id = "10"
        location_id = "4"
    else:
        obj_type = e_proc_object.get("objType")
        level_id = e_proc_object.get("levelId")
        location_id = e_proc_object.get("locationId")
    logger.info(f"XML parsed successfully. objType: {obj_type}, levelId: {level_id}, locationId: {location_id}")

except (FileNotFoundError, ET.ParseError, Exception) as e:
    logger.error(f"Error during XML processing: {e}")
    exit()

# --- Step 1: Initialize a session ---
session = requests.Session()

# --- Step 2: Perform browser-like login ---
logger.info("Attempting browser-like login via DesktopDefault.aspx...")

initial_get_return_url_encoded = quote_plus(f"{ESPEC_MODEL_BASE_PATH}SpecificationManagement.aspx?AutoClose=1")
initial_get_login_url = f"{LOGIN_HOST}{ESPEC_MODEL_BASE_POMS_PATH}DesktopDefault.aspx?ReturnUrl={initial_get_return_url_encoded}"

try:
    logger.info(f"GETting login page for VIEWSTATEs: {initial_get_login_url}")
    login_page_response = session.get(initial_get_login_url, verify=False)
    login_page_response.raise_for_status()

    soup = BeautifulSoup(login_page_response.text, 'html.parser')

    login_form = soup.find('form', id='loginForm')
    if not login_form:
        logger.error("Could not find the login form with ID 'loginForm'.")
        exit()

    login_data = {}
    for hidden_input in login_form.find_all('input', type='hidden'):
        name = hidden_input.get('name')
        value = hidden_input.get('value', '')
        if name:
            login_data[name] = value

    login_data['txtUsername'] = USERNAME
    login_data['txtPassword'] = PASSWORD
    login_data['__EVENTTARGET'] = 'XbtnLogin'
    login_data['__EVENTARGUMENT'] = ''

    form_action_url = login_form.get('action')
    if not form_action_url:
        logger.error("Login form does not have an 'action' attribute.")
        exit()

    post_login_url = urljoin(initial_get_login_url, form_action_url)
    logger.info(f"POSTing login data to: {post_login_url}")

    login_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": initial_get_login_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/533.36"
    }

    logger.debug(f"Login data being sent: {login_data}") # Use debug for sensitive info
    login_response = session.post(post_login_url, data=login_data, headers=login_headers, allow_redirects=True, verify=False)
    login_response.raise_for_status()

    if LOGIN_PAGE_RELATIVE_PATH in login_response.url or "POMSnet Login" in login_response.text:
        logger.error("Login failed. Check username, password, or server status.")
        logger.error(f"Login Response Status Code: {login_response.status_code}")
        logger.error(f"Login Response Content (start):\n{login_response.text[:1000]}...")
        exit()
    else:
        logger.info(f"Browser-like login successful! Current URL after login: {login_response.url}")
        logger.debug(f"Session cookies after login: {session.cookies.get_dict()}")

except requests.exceptions.RequestException as e:
    logger.error(f"Browser-like login request failed: {e}")
    exit()
except Exception as e:
    logger.error(f"An unexpected error occurred during browser-like login: {e}")
    exit()

### File Upload Process

# ```
# This section handles the crucial step of uploading your XML file to the server. We'll perform a **single file upload** (no chunking), which simplifies the process and was identified as a potential solution to earlier issues.

# ```python
# --- Step 3: Perform Single File Upload (No Chunking) ---
logger.info(f"Initiating single file upload for '{xml_file_name}' to {FILE_UPLOAD_URL}...")

uploaded_file_uid = str(uuid.uuid4())
total_file_size_actual = os.path.getsize(xml_file_path)

temp_server_filename = None

try:
    with open(xml_file_path, 'rb') as f:
        full_file_content = f.read()

        metadata = {
            "chunkIndex": 0,
            "contentType": "text/xml",
            "fileName": xml_file_name,
            "relativePath": xml_file_name,
            "totalFileSize": total_file_size_actual,
            "totalChunks": 1,
            "uploadUid": uploaded_file_uid
        }

        upload_files = {
            'files': ("blob", full_file_content, 'application/octet-stream'),
            'metadata': (None, json.dumps(metadata), 'application/json')
        }

        upload_headers = {
            'Accept': '*/*; q=0.5, application/json',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Host': LOGIN_HOST.split('//')[1],
            'Origin': LOGIN_HOST,
            'Referer': f"http://win-bkblmqnn8d9/poms/Apps/especwebapplication/SpecificationManagement.aspx",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }

        logger.info(f"Uploading entire file as a single chunk (UID: {uploaded_file_uid})...")
        upload_response = session.post(FILE_UPLOAD_URL, files=upload_files, headers=upload_headers, verify=False)
        upload_response.raise_for_status()

        upload_result = upload_response.json()
        logger.debug(f"Single upload response: {upload_result}")

        if upload_result.get("uploaded", False):
            logger.info("File uploaded successfully to server temp directory!")
            temp_server_filename = upload_result.get("TempFileName")
            uploaded_file_uid = upload_result.get("fileUid")
            if uploaded_file_uid is None:
                logger.warning("'fileUid' was not returned in the upload response. This might cause issues.")
        else:
            logger.error(f"File failed to upload. Response: {upload_result}")
            exit()

    if not temp_server_filename:
        logger.error("File upload completed but no TempFileName was received from the server.")
        exit()

    logger.info(f"Full file uploaded successfully. Server temporary path: {temp_server_filename}")

except requests.exceptions.RequestException as e:
    logger.error(f"File upload request failed: {e}")
    if hasattr(e, 'response') and e.response is not None:
        logger.error(f"Response Status Code: {e.response.status_code}")
        logger.error(f"Response Content: {e.response.text}")
    exit()
except Exception as e:
    logger.error(f"An unexpected error occurred during file upload: {e}")
    exit()

# ---

### Import and Local Cleanup

# After a successful upload, this section proceeds with calling the server's import function. If the import is successful, it will then **delete the local `scratch.xml` file** to save space on your machine.

# ```python
# --- Step 4: Call ImportFiles with the uploaded file's Uid ---
logger.info(f"Attempting to call ImportFiles with uploaded file UID: {uploaded_file_uid}...")

file_entry = {
    "FileName": xml_file_name,
    "Extension": os.path.splitext(xml_file_name)[1],
    "Size": file_size,
    "Uid": uploaded_file_uid
}

pass_data_json = {
    "userID":"administrator",
    "TreeIdentifier":"accf9c3b-1691-4e1a-b548-58c72e1db63c",
    "Domain":"",
    "DLL":"POMS_ProcObject_Lib",
    "Type": obj_type,
    "SubType":"PM_RECIPE",
    "Level": level_id,
    "Location": location_id,
    "Folder":"",
    "SearchSubType":"",
    "Files":[file_entry],
    "Signature":{
        "SignatureRequired":False,
        "UserID":"administrator",
        "UserName":"administrator",
        "Reason":"Import",
        "ISOTimestamp": datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
        "UserID2":"","UserName2":"","Comment":""
    },
    "ValidateXMLOnly":False,
    "StopOnError":False,
    "PreserveCheckinCheckout":False,
    "PreserveVersion":False,
    "PreserveStatus":False,
    "CreateFolders":False,
    "ImportBase":True,
    "ImportPhases":False
}

headers_for_import = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'http://win-bkblmqnn8d9',
    'Referer': 'http://win-bkblmqnn8d9/poms/Apps/especwebapplication/SpecificationManagement.aspx',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

try:
    response = session.post(IMPORT_URL, json=pass_data_json, headers=headers_for_import, verify=False)
    response.raise_for_status()

    result = response.json()
    logger.info("Import request successful!")
    logger.debug(f"Response JSON: {json.dumps(result, indent=2)}")

    # --- Step 5: Check import status and delete local file ---
    if result.get("d", {}).get("Success"):
        logger.info("Import reported success.")
        # Attempt to delete the local XML file
        try:
            if os.path.exists(xml_file_path):
                os.remove(xml_file_path)
                logger.info(f"Successfully deleted local file: {xml_file_path}")
            else:
                logger.warning(f"Local file not found at '{xml_file_path}', no need to delete.")
        except OSError as e:
            logger.error(f"Error deleting local file '{xml_file_path}': {e}")
    else:
        logger.warning("Import was not successful, local file will not be deleted.")


except requests.exceptions.HTTPError as errh:
    logger.error(f"HTTP Error during import: {errh}")
    logger.error(f"Response Status Code: {response.status_code}")
    logger.error(f"Response Content: {response.text}")
except requests.exceptions.ConnectionError as errc:
    logger.error(f"Error Connecting during import: {errc}")
except requests.exceptions.Timeout as errt:
    logger.error(f"Timeout Error during import: {errt}")
except requests.exceptions.RequestException as err:
    logger.error(f"An unexpected error occurred during import: {err}")