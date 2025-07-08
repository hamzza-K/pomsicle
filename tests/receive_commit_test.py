import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin, urlparse, parse_qs
import requests

# Start a session
session = requests.Session()


username = "administrator"
password = "Karachi@123"
login_host = "http://win-bkblmqnn8d9"
login_path = "/poms/DesktopDefault.aspx"
return_url = quote_plus("/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx")

login_url = f"{login_host}{login_path}?ReturnUrl={return_url}"
webmethod_url = "http://win-bkblmqnn8d9/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx/InitiateWorkSheet"

# --- Start session ---
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


payload = {
    "pfcValue": "659B4FC5-6747-4C0A-A3A0-DA694DD10B2D",
    "elementValue": "BE14CC69-F819-48C3-986D-768D04D71555",
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


# Payload

commit_url = "http://win-bkblmqnn8d9/poms/Apps/MaterialManagement/Receiving/UI/MiscBulkReceipt.aspx/Commit"

# Headers (important: Content-Type must be application/json)
headers = {
    "Content-Type": "application/json",
}

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
    
    "elementId": "3BE6B083-89EC-4E89-A1E5-0DF740B01E29",
    "instanceId": "Receive Material",
    "pfcId": "E0899EF8-C995-40C5-950C-F8F06491522B",
}

# Make POST request
response = session.post(commit_url, headers=headers, json=payload)

# Print response
print("Status Code:", response.status_code)
print("Response Body:", response.text)

