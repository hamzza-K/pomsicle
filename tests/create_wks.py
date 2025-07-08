from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, quote_plus
from urllib.parse import urlparse, parse_qs

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

# --- Step 2: Prepare WebMethod call ---
webmethod_headers = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0"
}

payload = {
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

webmethod_resp = session.post(
    webmethod_url,
    headers=webmethod_headers,
    data=json.dumps(payload)
)



# --- Step 3: Handle response ---
if webmethod_resp.ok:
    try:
        outer = webmethod_resp.json()
        result = json.loads(outer["d"])  # ASP.NET wraps result in `d`

        page_url = result.get("pageUrl", "")
        parsed_url = urlparse(page_url)
        query_params = parse_qs(parsed_url.query)
        worksheet_pfc_guid = query_params.get("_PFCGUID", [""])[0]
        print(f"[✅] Extracted _PFCGUID: {worksheet_pfc_guid}")

    except Exception as e:
        print("[❌] Could not parse result:", e)
        print(webmethod_resp.text[:1000])
else:
    print("[❌] WebMethod call failed:", webmethod_resp.status_code)
    print(webmethod_resp.text[:1000])



with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()

    # Inject cookies
    cookies = session.cookies.get_dict()
    playwright_cookies = [{
        'name': k,
        'value': v,
        'domain': 'win-bkblmqnn8d9',
        'path': '/',
        'httpOnly': True,
        'secure': False,
        'sameSite': 'Lax',
    } for k, v in cookies.items()]

    context.add_cookies(playwright_cookies)

    page = context.new_page()

    # Setup request logging


    target_url = None
    pfc_val = None
    element_val = None

    def on_request(request):
        global target_url, pfc_val, element_val

        url = request.url
        if "MiscBulkReceipt.aspx" in url and "__PFC=" in url:
            target_url = url
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)

            pfc_val = query_params.get("__PFC", [""])[0]
            element_val = query_params.get("__ELEMENT", [""])[0]

            print(f"[MATCHED] {url}")
            print(f"[✅ __PFC]: {pfc_val}")
            print(f"[✅ __ELEMENT]: {element_val}")

    page.on("request", on_request)


    # Go to the base page
    page.goto(f"{login_host}/poms/Apps/RecipeExecution/ActionList/UI/ActionList.aspx?_PFCGUID={worksheet_pfc_guid}&RECIPETYPE=Worksheet")

    print("[INFO] Waiting for dynamic content to load...")
    page.wait_for_timeout(10000)  # 10 seconds

    if not pfc_val or not element_val:
        print("[❌] __PFC or __ELEMENT not found in requests.")

    browser.close()



    


# Reuse existing authenticated session from earlier steps
# Example URL to match your system's WebMethod endpoint
validate_url = "http://win-bkblmqnn8d9/poms/Apps/MaterialManagement/Receiving/UI/MiscBulkReceipt.aspx/ValidateData"

# Payload based on the JavaScript function and your provided values
payload = {
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

# Headers for ASP.NET AJAX WebMethod call
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0"
}

# Make the POST request using authenticated session
response = session.post(validate_url, data=json.dumps(payload), headers=headers)

# Handle response
if response.ok:
    try:
        outer = response.json()
        result = json.loads(outer["d"])
        print("[✅] Validation successful.")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print("[❌] Failed to parse response:", e)
        print(response.text[:500])
else:
    print("[❌] WebMethod call failed:", response.status_code)
    print(response.text[:500])



# Target URL
signoff_url = "http://win-bkblmqnn8d9/POMS/apps/Utilities/Security/UI/SignOff.aspx/SubmitSignOff"

# Example session (you should reuse the authenticated `requests.Session` you already have)
session.verify = False  # Skip SSL checks if internal or self-signed

# WebMethod headers
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0"
}

# Constructing the payload (fill in actual values as needed)
payload = {
    "pfcValue": pfc_val,
    "elementValue": element_val,
    "signTypeValue": "2",  # or "Verification", "Approval", etc.
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
    "strIsDialog": "false",
    "currWorkSheetValue": "",
    "uniqueId": "signOffForm",
    "strBypassSignoff": "false",  # set "false" if you want real signoff
    "pageName": "MiscBulkReceipt.aspx"
}

# Send the POST request
response = session.post(signoff_url, headers=headers, data=json.dumps(payload))

# Handle response
if response.ok:
    try:
        outer = response.json()
        result = json.loads(outer["d"])
        print("[✅] SignOff result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print("[❌] Failed to parse response:", e)
        print(response.text[:500])
else:
    print("[❌] SignOff WebMethod call failed:", response.status_code)
    print(response.text[:500])




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


payload = {
    "materialId": "1112",
    "enteredLotId": "",
    "newLotId": "L000000472",
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
    "pfcId": pfc_val,
}


commit_url = "http://win-bkblmqnn8d9/poms/Apps/MaterialManagement/Receiving/UI/MiscBulkReceipt.aspx/Commit"

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0"
}

response = session.post(commit_url, headers=headers, data=json.dumps(payload))

if response.ok:
    try:
        outer = response.json()
        result = json.loads(outer["d"])
        if not result["hasErrors"]:
            final = json.loads(result["data"])
            print("[✅] Commit successful.")
            print(json.dumps(final, indent=2))
        else:
            print("[❌] Server returned errors:")
            print(json.dumps(result, indent=2))
    except Exception as e:
        print("[❌] Failed to parse response:", e)
        print(response.text[:500])
else:
    print("[❌] Commit WebMethod call failed:", response.status_code)
    print(response.text[:500])

