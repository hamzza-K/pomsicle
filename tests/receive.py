import json
import logging
from urllib.parse import quote_plus, urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

username = "administrator"
password = "Karachi@123"
login_host = "http://win-bkblmqnn8d9"
login_path = "/poms/DesktopDefault.aspx"
return_url = quote_plus("/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx")
login_url = f"{login_host}{login_path}?ReturnUrl={return_url}"

session = requests.Session()
session.verify = False

resp = session.get(login_url)
soup = BeautifulSoup(resp.text, "html.parser")
form = soup.find("form", id="loginForm")

login_data = {
    input_tag.get("name"): input_tag.get("value", "")
    for input_tag in form.find_all("input")
    if input_tag.get("name")
}
login_data["txtUsername"] = username
login_data["txtPassword"] = password
login_data["__EVENTTARGET"] = "XbtnLogin"
login_data["__EVENTARGUMENT"] = ""

post_url = urljoin(login_url, form.get("action"))
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": login_url,
    "User-Agent": "Mozilla/5.0"
}
login_resp = session.post(post_url, data=login_data, headers=headers, allow_redirects=True)

if "login" in login_resp.url.lower():
    logging.error("Login failed.")
    exit()
logging.info("Login successful.")

worksheet_url = "http://win-bkblmqnn8d9/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx/InitiateWorkSheet"
worksheet_payload = {
    "hUnitProcedureId": "",
    "hOrderId": "",
    "hBatchId": "",
    "hSplitId": "",
    "sWorksheetId": "Receiving",
    "sVersion": "5.001",
    "sUnitProcedure": "ReceivingUP1",
    "sUnitClass": "ReceivingArea",
    "cmbUnitClass": "Bay1",
    "hWorkSheetStartedFrom": "",
    "isQsWksId": "false",
    "inEbr": False
}
webmethod_headers = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0"
}

r = session.post(worksheet_url, headers=webmethod_headers, data=json.dumps(worksheet_payload))

try:
    worksheet_data = json.loads(r.json()["d"])
    page_url = worksheet_data["pageUrl"]
    pfc_guid = parse_qs(urlparse(page_url).query).get("_PFCGUID", [""])[0]
    logging.info(f"Extracted _PFCGUID: {pfc_guid}")
except Exception as e:
    logging.error(f"Failed to extract _PFCGUID: {e}")
    exit()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies([
        {
            'name': k,
            'value': v,
            'domain': 'win-bkblmqnn8d9',
            'path': '/',
            'httpOnly': True,
            'secure': False,
            'sameSite': 'Lax',
        } for k, v in session.cookies.get_dict().items()
    ])
    page = context.new_page()

    target_url = pfc_val = element_val = None

    def on_request(request):
        global target_url, pfc_val, element_val
        url = request.url
        if "MiscBulkReceipt.aspx" in url and "__PFC=" in url:
            target_url = url
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            pfc_val = query_params.get("__PFC", [""])[0]
            element_val = query_params.get("__ELEMENT", [""])[0]
            logging.info(f"Captured request to: {url}")
            logging.info(f"__PFC: {pfc_val}, __ELEMENT: {element_val}")

    page.on("request", on_request)
    page.goto(f"{login_host}/poms/Apps/RecipeExecution/ActionList/UI/ActionList.aspx?_PFCGUID={pfc_guid}&RECIPETYPE=Worksheet")
    logging.info("Waiting for browser to trigger WebMethod request...")
    page.wait_for_timeout(10000)
    browser.close()

if not pfc_val or not element_val:
    logging.error("Could not extract __PFC or __ELEMENT from network activity.")
    exit()

validate_url = "http://win-bkblmqnn8d9/poms/Apps/MaterialManagement/Receiving/UI/MiscBulkReceipt.aspx/ValidateData"
validate_payload = {
    "materialId": "1112",
    "uomId": "l",
    "noOfContainers": 1,
    "qtyPerContainer": 1,
    "dateExpire": "7/7/2030 6:34:28 PM",
    "dateRetest": "12/25/2027 6:34:28 PM",
    "lotId": "",
    "isNewLot": True,
    "vendorLotId": "",
    "isBulk": False,
    "vesselId": "",
    "areaId": "Bulk Dry Tank 1",
    "locationId": "Outlet D11",
    "plantId": "Herndon",
    "checkNewLot": True,
    "GenerateNewLotID": True
}
response = session.post(validate_url, data=json.dumps(validate_payload), headers=webmethod_headers)
if response.ok:
    try:
        outer = response.json()
        result = json.loads(outer["d"])
        nested_data = json.loads(result["data"])
        lot_id = nested_data["lotId"]
        logging.debug(f"lotId retrieved: {lot_id}")
        logging.info("Validation successful.")
    except Exception as e:
        logging.error(f"Failed to parse validation response: {e}")
else:
    logging.error(f"Validation request failed: {response.status_code}")



signoff_url = "http://win-bkblmqnn8d9/POMS/apps/Utilities/Security/UI/SignOff.aspx/SubmitSignOff"
signoff_payload = {
    "pfcValue": pfc_val,
    "elementValue": element_val,
    "signTypeValue": "2",
    "optrObjClassValue": "ReceivingOperator",
    "verObjClassValue": "ReceivingVerifier",
    "secActionValue": "MiscBulkReceipt",
    "primeUserIdValue": "administrator",
    "fetchReasonValue": "",
    "commentText": "",
    "firstUserText": "administrator",
    "identityNameValue": "administrator",
    "dsUserNameText": "",
    "secondUserText": "",
    "dsVerNameDescText": "",
    "firstPassText": "Karachi@123",
    "dsReasonText": "",
    "strIsDialog": "true",
    "currWorkSheetValue": "",
    "uniqueId": "signOffForm",
    "strBypassSignoff": "false",
    "pageName": "MiscBulkReceipt.aspx"
}
response = session.post(signoff_url, headers=webmethod_headers, data=json.dumps(signoff_payload))
if response.ok:
    try:
        result = json.loads(response.json()["d"])
        logging.info("SignOff successful.")
    except Exception as e:
        logging.error(f"Failed to parse signoff response: {e}")
else:
    logging.error(f"SignOff WebMethod call failed: {response.status_code}")


commit_url = "http://win-bkblmqnn8d9/poms/Apps/MaterialManagement/Receiving/UI/MiscBulkReceipt.aspx/Commit"
commit_payload = {
    "materialId": "1112",
    "enteredLotId": "",
    "newLotId": lot_id,
    "uomId": "l",
    "isBulk": False,
    "isNewLot": True,
    "vendorLotId": "",
    "noOfContainers": 1,
    "qtyPerContainer": 1,
    "areaId": "Bulk Dry Tank 1",
    "locationId": "Outlet D11",
    "vesselId": "",
    "dateExpire": "7/7/2030 6:34:28 PM",
    "dateRetest": "12/25/2027 6:34:28 PM",
    "plantId": "Herndon",
    "exceptionId": "",
    "LabelGroupKey": "labelGroupf9561bd6-db77-4d43-a7af-eb299a3fc5c2",
    "vesselEquipmentClass": "",
    "elementId": element_val,
    "instanceId": "Receive Material",
    "pfcId": pfc_val
}
response = session.post(commit_url, headers=webmethod_headers, data=json.dumps(commit_payload))
if response.ok:
    try:
        outer = response.json()
        result = json.loads(outer["d"])
        nested_data = json.loads(result["data"])

        print(nested_data["Containers"])
        if not result["hasErrors"]:
            logging.info("Commit successful.")

        else:
            logging.warning(f"Commit returned errors: {result}")
    except Exception as e:
        logging.error(f"Failed to parse commit response: {e}")
else:
    logging.error(f"Commit WebMethod call failed: {response.status_code}")

