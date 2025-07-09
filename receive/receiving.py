import json
import logging
from urllib.parse import quote_plus, urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

import polars

# Setup logging
logger = logging.getLogger(__name__)

class ReceiveManager:
    """Class to manage receiving operations in POMS system."""

    def __init__(self, settings: dict, settings_receive: dict, username: str, password: str):
        """
        Initialize the ReceiveManager with settings and credentials.
        """
        self.settings = settings
        self.username = username
        self.password = password
        
        self.base_app_url = settings.get('BASE_APP_URL')
        self.import_url = settings.get('IMPORT_URL')
        self.login_host = settings.get('LOGIN_HOST')
        self.login_page_relative_path = settings.get('LOGIN_PAGE_RELATIVE_PATH')
        self.machine_name = settings.get('MACHINE_NAME')
        self.program_path = settings.get('PROGRAM_BASE_PATH')

        self.material_id = settings_receive.get('MATERIAL_ID', '1112')
        self.uom_id = settings_receive.get('UOM_ID', 'g')
        self.containers = settings_receive.get('CONTAINERS', 1)
        self.qty_per_container = settings_receive.get('QTY_PER_CONTAINER', 1)
        self.area_id = settings_receive.get('AREA_ID', 'Bulk Dry Tank 1')
        self.location_id = settings_receive.get('LOCATION_ID', 'Outlet D11')
        self.plant_id = settings_receive.get('PLANT_ID', 'Herndon')


        self.lot_id = None
        self.recieved_containers = list()

        self.target_url = self.pfc_val = self.element_val = None
        
        
        if not all([self.username, self.password, self.machine_name, self.base_app_url,
                   self.login_host]):
            logger.critical("Missing essential configuration variables in settings. Exiting.")
            raise ValueError("Missing essential configuration variables for PomsicleTemplateManager.")

        self.session = requests.Session()
        self.session.verify = False

    def _perform_login(self) -> bool:
        """
        Performs a browser-like login to the POMSicle system.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        logger.info("Starting browser-like login process...")

        try:
            return_url = quote_plus("/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx")
            login_url = f"{self.login_host}{self.login_page_relative_path}?ReturnUrl={return_url}"
            logger.debug(f"Constructed login URL: {login_url}")

            resp = self.session.get(login_url)
            logger.debug(f"GET request to login page returned status code: {resp.status_code}")

            soup = BeautifulSoup(resp.text, "html.parser")
            form = soup.find("form", id="loginForm")
            if not form:
                logger.error("Login form not found in the response.")
                return False

            login_data = {
                input_tag.get("name"): input_tag.get("value", "")
                for input_tag in form.find_all("input")
                if input_tag.get("name")
            }
            login_data.update({
                "txtUsername": self.username,
                "txtPassword": self.password,
                "__EVENTTARGET": "XbtnLogin",
                "__EVENTARGUMENT": ""
            })

            post_url = urljoin(login_url, form.get("action"))
            logger.debug(f"Posting login credentials to: {post_url}")

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": login_url,
                "User-Agent": "Mozilla/5.0"
            }

            login_resp = self.session.post(post_url, data=login_data, headers=headers, allow_redirects=True)
            logger.debug(f"POST request for login returned status code: {login_resp.status_code}")
            logger.debug(f"Final redirected URL: {login_resp.url}")

            if "login" in login_resp.url.lower():
                logger.error("Login failed. Credentials may be incorrect or server rejected the login.")
                return False

            logger.info("Login successful.")
            return True

        except Exception as e:
            logger.exception(f"Exception occurred during login: {e}")
            return False


    def _worksheet_initiation(self) -> str:
        """
        Initiates the worksheet for receiving materials.

        Returns:
            str: The page URL where the worksheet is initiated.
        """
        worksheet_url = f"{self.login_host}/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx/InitiateWorkSheet"
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

        r = self.session.post(worksheet_url, headers=webmethod_headers, data=json.dumps(worksheet_payload))

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
                } for k, v in self.session.cookies.get_dict().items()
            ])
            page = context.new_page()

            def on_request(request):
                url = request.url
                if "MiscBulkReceipt.aspx" in url and "__PFC=" in url:
                    self.target_url = url
                    parsed = urlparse(url)
                    query_params = parse_qs(parsed.query)
                    self.pfc_val = query_params.get("__PFC", [""])[0]
                    self.element_val = query_params.get("__ELEMENT", [""])[0]
                    logging.info(f"Captured request to: {url}")
                    logging.info(f"__PFC: {self.pfc_val}, __ELEMENT: {self.element_val}")

            page.on("request", on_request)
            page.goto(f"{self.login_host}/poms/Apps/RecipeExecution/ActionList/UI/ActionList.aspx?_PFCGUID={pfc_guid}&RECIPETYPE=Worksheet")
            logging.info("Waiting for browser to trigger WebMethod request...")
            page.wait_for_timeout(10000)
            browser.close()

        if not self.pfc_val or not self.element_val:
            logging.error("Could not extract __PFC or __ELEMENT from network activity.")
            exit()

        logger.info(f"PFC Value: {self.pfc_val}, Element Value: {self.element_val}")

    def _validate_data(self, material_id: str, uom: str, containers: int, qty_containers: int) -> dict:

        validate_url = f"{self.login_host}/poms/Apps/MaterialManagement/Receiving/UI/MiscBulkReceipt.aspx/ValidateData"

        validate_payload = {
            "materialId": material_id,
            "uomId": uom,
            "noOfContainers": containers,
            "qtyPerContainer": qty_containers,
            "dateExpire": "7/7/2030 6:34:28 PM",
            "dateRetest": "12/25/2027 6:34:28 PM",
            "lotId": "",
            "isNewLot": True,
            "vendorLotId": "",
            "isBulk": False,
            "vesselId": "",
            "areaId": self.area_id,
            "locationId": self.location_id,
            "plantId": self.plant_id,
            "checkNewLot": True,
            "GenerateNewLotID": True
        }

        webmethod_headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0"
        }


        response = self.session.post(validate_url, data=json.dumps(validate_payload), headers=webmethod_headers)
        if response.ok:
            try:
                outer = response.json()
                result = json.loads(outer["d"])
                nested_data = json.loads(result["data"])
                lot_id = nested_data["lotId"]
                self.lot_id = lot_id
                logging.debug(f"lotId retrieved: {lot_id}")
                logging.info("Validation successful.")
            except Exception as e:
                logging.error(f"Failed to parse validation response: {e}")
        else:
            logging.error(f"Validation request failed: {response.status_code}")

    def _submit_signoff(self) -> bool:
        
        signoff_url = f"{self.login_host}/POMS/apps/Utilities/Security/UI/SignOff.aspx/SubmitSignOff"

        signoff_payload = {
            "pfcValue": self.pfc_val,
            "elementValue": self.element_val,
            "signTypeValue": "2",
            "optrObjClassValue": "ReceivingOperator",
            "verObjClassValue": "ReceivingVerifier",
            "secActionValue": "MiscBulkReceipt",
            "primeUserIdValue": self.username,
            "fetchReasonValue": "",
            "commentText": "",
            "firstUserText": self.username,
            "identityNameValue": self.username,
            "dsUserNameText": "",
            "secondUserText": "",
            "dsVerNameDescText": "",
            "firstPassText": self.password,
            "dsReasonText": "",
            "strIsDialog": "true",
            "currWorkSheetValue": "",
            "uniqueId": "signOffForm",
            "strBypassSignoff": "false",
            "pageName": "MiscBulkReceipt.aspx"
        }
        
        
        webmethod_headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0"
        }

        response = self.session.post(signoff_url, headers=webmethod_headers, data=json.dumps(signoff_payload))
        if response.ok:
            try:
                result = json.loads(response.json()["d"])
                logging.debug(f"SignOff result: {result}")
                logging.info("SignOff successful.")
            except Exception as e:
                logging.error(f"Failed to parse signoff response: {e}")
        else:
            logging.error(f"SignOff WebMethod call failed: {response.status_code}")

    def _commit(self, material_id: str, uom: str, containers: int, qty_per_container: int) -> None:
        
        commit_url = f"{self.login_host}/poms/Apps/MaterialManagement/Receiving/UI/MiscBulkReceipt.aspx/Commit"
        commit_payload = {
            "materialId": material_id,
            "enteredLotId": "",
            "newLotId": self.lot_id,
            "uomId": uom,
            "isBulk": False,
            "isNewLot": True,
            "vendorLotId": "",
            "noOfContainers": containers,
            "qtyPerContainer": qty_per_container,
            "areaId": "Bulk Dry Tank 1", # TODO Change this
            "locationId": "Outlet D11", # TODO Change this
            "vesselId": "",
            "dateExpire": "7/7/2030 6:34:28 PM",
            "dateRetest": "12/25/2027 6:34:28 PM",
            "plantId": "Herndon",
            "exceptionId": "",
            "LabelGroupKey": "labelGroupf9561bd6-db77-4d43-a7af-eb299a3fc5c2",
            "vesselEquipmentClass": "",
            "elementId": self.element_val,
            "instanceId": "Receive Material",
            "pfcId": self.pfc_val
        }
        
        webmethod_headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0"
        }

        response = self.session.post(commit_url, headers=webmethod_headers, data=json.dumps(commit_payload))
        if response.ok:
            try:
                outer = response.json()
                result = json.loads(outer["d"])
                nested_data = json.loads(result["data"])

                self.recieved_containers = nested_data["Containers"]

                if not result["hasErrors"]:
                    logging.info("Commit successful.")

                else:
                    logging.warning(f"Commit returned errors: {result}")
            except Exception as e:
                logging.error(f"Failed to parse commit response: {e}")
        else:
            logging.error(f"Commit WebMethod call failed: {response.status_code}")



    def receive(self, material_name: str, uom: str, containers: int, qty_per_container: int) -> bool:
        logger.info("Starting receiving process...")

        if not self._perform_login():
            logger.error("Login failed. Cannot proceed with receiving.")
            return False

        self._worksheet_initiation()
        self._validate_data(material_id=material_name, uom=uom, containers=containers, qty_containers=qty_per_container)
        self._submit_signoff()
        self._commit(material_id=material_name, uom=uom, containers=containers, qty_per_container=qty_per_container)

        logger.info("Receiving process completed successfully.")

        list_conts = []
        for container in self.recieved_containers:
            list_conts.append({
                "containers": str(container),
                "material_name": material_name,
                "uom": uom,
                "qty_per_container": qty_per_container,
                "lot_id": self.lot_id,
                "area_id": self.area_id,
                "location_id": self.location_id,
            })


        df = polars.DataFrame(list_conts)

        print(df)

        return True


    

# username = "administrator"
# password = "Karachi@123"
# login_host = "http://win-bkblmqnn8d9"
# login_path = "/poms/DesktopDefault.aspx"
# return_url = quote_plus("/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx")
# login_url = f"{login_host}{login_path}?ReturnUrl={return_url}"

# session = requests.Session()
# session.verify = False

# resp = session.get(login_url)
# soup = BeautifulSoup(resp.text, "html.parser")
# form = soup.find("form", id="loginForm")

# login_data = {
#     input_tag.get("name"): input_tag.get("value", "")
#     for input_tag in form.find_all("input")
#     if input_tag.get("name")
# }
# login_data["txtUsername"] = username
# login_data["txtPassword"] = password
# login_data["__EVENTTARGET"] = "XbtnLogin"
# login_data["__EVENTARGUMENT"] = ""

# post_url = urljoin(login_url, form.get("action"))
# headers = {
#     "Content-Type": "application/x-www-form-urlencoded",
#     "Referer": login_url,
#     "User-Agent": "Mozilla/5.0"
# }
# login_resp = session.post(post_url, data=login_data, headers=headers, allow_redirects=True)

# if "login" in login_resp.url.lower():
#     logging.error("Login failed.")
#     exit()
# logging.info("Login successful.")

# worksheet_url = "http://win-bkblmqnn8d9/poms/Apps/RecipeExecution/Worksheet/UI/InitiateWorksheet.aspx/InitiateWorkSheet"
# worksheet_payload = {
#     "hUnitProcedureId": "",
#     "hOrderId": "",
#     "hBatchId": "",
#     "hSplitId": "",
#     "sWorksheetId": "Receiving",
#     "sVersion": "5.001",
#     "sUnitProcedure": "ReceivingUP1",
#     "sUnitClass": "ReceivingArea",
#     "cmbUnitClass": "Bay1",
#     "hWorkSheetStartedFrom": "",
#     "isQsWksId": "false",
#     "inEbr": False
# }
# webmethod_headers = {
#     "Content-Type": "application/json; charset=utf-8",
#     "X-Requested-With": "XMLHttpRequest",
#     "User-Agent": "Mozilla/5.0"
# }

# r = session.post(worksheet_url, headers=webmethod_headers, data=json.dumps(worksheet_payload))

# try:
#     worksheet_data = json.loads(r.json()["d"])
#     page_url = worksheet_data["pageUrl"]
#     pfc_guid = parse_qs(urlparse(page_url).query).get("_PFCGUID", [""])[0]
#     logging.info(f"Extracted _PFCGUID: {pfc_guid}")
# except Exception as e:
#     logging.error(f"Failed to extract _PFCGUID: {e}")
#     exit()

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=True)
#     context = browser.new_context()
#     context.add_cookies([
#         {
#             'name': k,
#             'value': v,
#             'domain': 'win-bkblmqnn8d9',
#             'path': '/',
#             'httpOnly': True,
#             'secure': False,
#             'sameSite': 'Lax',
#         } for k, v in session.cookies.get_dict().items()
#     ])
#     page = context.new_page()

#     target_url = pfc_val = element_val = None

#     def on_request(request):
#         global target_url, pfc_val, element_val
#         url = request.url
#         if "MiscBulkReceipt.aspx" in url and "__PFC=" in url:
#             target_url = url
#             parsed = urlparse(url)
#             query_params = parse_qs(parsed.query)
#             pfc_val = query_params.get("__PFC", [""])[0]
#             element_val = query_params.get("__ELEMENT", [""])[0]
#             logging.info(f"Captured request to: {url}")
#             logging.info(f"__PFC: {pfc_val}, __ELEMENT: {element_val}")

#     page.on("request", on_request)
#     page.goto(f"{login_host}/poms/Apps/RecipeExecution/ActionList/UI/ActionList.aspx?_PFCGUID={pfc_guid}&RECIPETYPE=Worksheet")
#     logging.info("Waiting for browser to trigger WebMethod request...")
#     page.wait_for_timeout(10000)
#     browser.close()

# if not pfc_val or not element_val:
#     logging.error("Could not extract __PFC or __ELEMENT from network activity.")
#     exit()

# validate_url = "http://win-bkblmqnn8d9/poms/Apps/MaterialManagement/Receiving/UI/MiscBulkReceipt.aspx/ValidateData"
# validate_payload = {
#     "materialId": "1112",
#     "uomId": "l",
#     "noOfContainers": 10,
#     "qtyPerContainer": 10,
#     "dateExpire": "7/7/2030 6:34:28 PM",
#     "dateRetest": "12/25/2027 6:34:28 PM",
#     "lotId": "",
#     "isNewLot": True,
#     "vendorLotId": "",
#     "isBulk": False,
#     "vesselId": "",
#     "areaId": "Bulk Dry Tank 1",
#     "locationId": "Outlet D11",
#     "plantId": "Herndon",
#     "checkNewLot": True,
#     "GenerateNewLotID": True
# }
# response = session.post(validate_url, data=json.dumps(validate_payload), headers=webmethod_headers)
# if response.ok:
#     try:
#         outer = response.json()
#         result = json.loads(outer["d"])
#         nested_data = json.loads(result["data"])
#         lot_id = nested_data["lotId"]
#         logging.debug(f"lotId retrieved: {lot_id}")
#         logging.info("Validation successful.")
#     except Exception as e:
#         logging.error(f"Failed to parse validation response: {e}")
# else:
#     logging.error(f"Validation request failed: {response.status_code}")



# signoff_url = "http://win-bkblmqnn8d9/POMS/apps/Utilities/Security/UI/SignOff.aspx/SubmitSignOff"
# signoff_payload = {
#     "pfcValue": pfc_val,
#     "elementValue": element_val,
#     "signTypeValue": "2",
#     "optrObjClassValue": "ReceivingOperator",
#     "verObjClassValue": "ReceivingVerifier",
#     "secActionValue": "MiscBulkReceipt",
#     "primeUserIdValue": "administrator",
#     "fetchReasonValue": "",
#     "commentText": "",
#     "firstUserText": "administrator",
#     "identityNameValue": "administrator",
#     "dsUserNameText": "",
#     "secondUserText": "",
#     "dsVerNameDescText": "",
#     "firstPassText": "Karachi@123",
#     "dsReasonText": "",
#     "strIsDialog": "true",
#     "currWorkSheetValue": "",
#     "uniqueId": "signOffForm",
#     "strBypassSignoff": "false",
#     "pageName": "MiscBulkReceipt.aspx"
# }
# response = session.post(signoff_url, headers=webmethod_headers, data=json.dumps(signoff_payload))
# if response.ok:
#     try:
#         result = json.loads(response.json()["d"])
#         logging.info("SignOff successful.")
#     except Exception as e:
#         logging.error(f"Failed to parse signoff response: {e}")
# else:
#     logging.error(f"SignOff WebMethod call failed: {response.status_code}")


# commit_url = "http://win-bkblmqnn8d9/poms/Apps/MaterialManagement/Receiving/UI/MiscBulkReceipt.aspx/Commit"
# commit_payload = {
#     "materialId": "1112",
#     "enteredLotId": "",
#     "newLotId": lot_id,
#     "uomId": "l",
#     "isBulk": False,
#     "isNewLot": True,
#     "vendorLotId": "",
#     "noOfContainers": 10,
#     "qtyPerContainer": 10,
#     "areaId": "Bulk Dry Tank 1",
#     "locationId": "Outlet D11",
#     "vesselId": "",
#     "dateExpire": "7/7/2030 6:34:28 PM",
#     "dateRetest": "12/25/2027 6:34:28 PM",
#     "plantId": "Herndon",
#     "exceptionId": "",
#     "LabelGroupKey": "labelGroupf9561bd6-db77-4d43-a7af-eb299a3fc5c2",
#     "vesselEquipmentClass": "",
#     "elementId": element_val,
#     "instanceId": "Receive Material",
#     "pfcId": pfc_val
# }
# response = session.post(commit_url, headers=webmethod_headers, data=json.dumps(commit_payload))
# if response.ok:
#     try:
#         outer = response.json()
#         result = json.loads(outer["d"])
#         nested_data = json.loads(result["data"])

#         print(nested_data["Containers"])
#         if not result["hasErrors"]:
#             logging.info("Commit successful.")

#         else:
#             logging.warning(f"Commit returned errors: {result}")
#     except Exception as e:
#         logging.error(f"Failed to parse commit response: {e}")
# else:
#     logging.error(f"Commit WebMethod call failed: {response.status_code}")

