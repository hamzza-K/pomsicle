from typing import Optional
import requests
import json
import xml.etree.ElementTree as ET
import os
import logging
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from banners import Banner
import ast
import uuid
from utils.parse_date import parse_poms_date as parse_date

logger = logging.getLogger(__name__)

class PomsicleMaterialManager:
    """
    Manages the creation, modification, and upload of Material XML files to POMSicle.
    """
    def __init__(self, settings: dict, material_settings: dict, location_settings: dict, username: str, password: str):
        """
        Initializes the PomsicleMaterialManager with configuration settings and credentials.

        Args:
            settings (dict): A dictionary containing POMSicle configuration details
                             (e.g., MACHINE_NAME, BASE_APP_URL).
            material_settings (dict): Material-specific settings (level_id, location_id, location_name).
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

        if not isinstance(self.machine_name, str) or not self.machine_name:
            logger.critical("MACHINE_NAME is not a valid string in settings. Exiting.")
            raise ValueError("MACHINE_NAME is not a valid string in settings.")

        if not isinstance(self.login_host, str) or not self.login_host:
            logger.critical("LOGIN_HOST is not a valid string in settings. Exiting.")
            raise ValueError("LOGIN_HOST is not a valid string in settings.")

        if not isinstance(self.base_app_url, str) or not self.base_app_url:
            logger.critical("BASE_APP_URL is not a valid string in settings. Exiting.")
            raise ValueError("BASE_APP_URL is not a valid string in settings.")

        if not isinstance(self.import_url, str) or not self.import_url:
            logger.critical("IMPORT_URL is not a valid string in settings. Exiting.")
            raise ValueError("IMPORT_URL is not a valid string in settings.")

        if not isinstance(self.file_upload_url, str) or not self.file_upload_url:
            logger.critical("FILE_UPLOAD_URL is not a valid string in settings. Exiting.")
            raise ValueError("FILE_UPLOAD_URL is not a valid string in settings.")
        
        self.level_id = location_settings.get('LEVEL_ID', '10')
        self.location_id = location_settings.get('LOCATION_ID', '4')
        self.location_name = location_settings.get('LOCATION_NAME', 'Herndon')

        self.session = requests.Session()
        self._is_logged_in = False
        
        self.file_upload_url = self.login_host + '/' + self.base_app_url + '/' + self.file_upload_url
        self.import_url = self.login_host + '/' + self.base_app_url + '/' + self.import_url

        self.login_page_relative_path = "/POMS/DesktopDefault.aspx"
        self.espec_model_base_path = "/poms/apps/eSpecWebApplication/"
        self.espec_model_base_poms_path = "/poms/"

        if not all([self.username, self.password, self.machine_name, self.base_app_url,
                    self.import_url, self.file_upload_url, self.login_host]):
            logger.critical("Missing essential configuration variables in settings. Exiting.")
            raise ValueError("Missing essential configuration variables for PomsicleMaterialManager.")
        
    def _perform_login(self) -> bool:
        """
        Performs a browser-like login to the POMSicle system.
        Only performs login if not already logged in.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        # Skip if already logged in
        if self._is_logged_in:
            logger.debug("Already logged in, skipping login attempt.")
            return True
            
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
                self._is_logged_in = False
                return False
            else:
                logger.info(f"Browser-like login successful! Current URL after login: {login_response.url}")
                logger.debug(f"Session cookies after login: {self.session.cookies.get_dict()}")
                self._is_logged_in = True
                return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Browser-like login request failed: {e}")
            self._is_logged_in = False
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during browser-like login: {e}")
            self._is_logged_in = False
            return False

    def _process_xml_file(self, xml_file_path: str):
        """
        Parses the XML file to extract objType, levelId, and locationId.

        Args:
            xml_file_path (str): Path to the XML file.

        Returns:
            tuple: (obj_type, level_id, location_id, file_size) or (None, None, None, None) on error.
        """
        if not os.path.exists(xml_file_path):
            logger.error(f"XML file not found at '{xml_file_path}'.")
            return None, None, None, None

        obj_type = ""
        level_id = ""
        location_id = ""
        file_size = os.path.getsize(xml_file_path)

        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            e_base_object = root.find(".//eBaseObject")

            if e_base_object is None:
                logger.warning("Could not find 'eBaseObject' element in the XML file. Using placeholder values.")
                obj_type = "MM_OBJ"
                level_id = self.level_id
                location_id = self.location_id
            else:
                obj_type = e_base_object.get("objType")
                level_id = e_base_object.get("levelId")
                location_id = e_base_object.get("locationId")
            logger.debug(f"XML parsed successfully. objType: {obj_type}, levelId: {level_id}, locationId: {location_id}")
            return obj_type, level_id, location_id, file_size

        except (FileNotFoundError, ET.ParseError, Exception) as e:
            logger.error(f"Error during XML processing: {e}")
            return None, None, None, None

    def _modify_template_xml(self, material_id: str, material_description: Optional[str | None], attributes: Optional[dict]) -> str:
        """
        Modifies the material template XML by setting material ID, description, and attribute values.
        Uses deep copies to ensure original template files are never modified.

        Args:
            material_id (str): ID for the material.
            material_description (str): Description for the material. If None, uses material_id.
            attributes (dict): Dictionary mapping attribId to sValue. e.g., {"Inventory Tracking": "Container", "Inventory UOM": "g"}
            
        Returns:
            str: Path to the modified XML file.
        """
        # Parse template file - this is read-only and will never be modified
        template_path = os.path.join(os.path.dirname(__file__), 'template', 'material_template.xml')
        
        if not os.path.exists(template_path):
            logger.error(f"Material template not found at: {template_path}")
            raise FileNotFoundError(f"Material template not found at: {template_path}")
        
        template = ET.parse(template_path)
        template_root = template.getroot()
        e_spec_xml_objs = template_root.find('eSpecXmlObjs')
        
        if e_spec_xml_objs is None:
            raise RuntimeError("Template does not contain <eSpecXmlObjs> element")
        
        # Find the eBaseObject (should be only one in material template)
        base_object = e_spec_xml_objs.find(".//eBaseObject[@objType='MM_OBJ']")
        
        if base_object is None:
            raise RuntimeError("Template does not contain <eBaseObject objType='MM_OBJ'> element")
        
        # Set material ID and description
        base_object.set('id', material_id)
        base_object.set('description', material_description or material_id + " Pomsicle")
        base_object.set('levelName', 'Master')
        base_object.set('levelId', self.level_id)
        base_object.set('locationName', self.location_name)
        base_object.set('locationId', self.location_id)
        base_object.set('objType', 'MM_OBJ')
        base_object.set('relObjType', 'MM')
        base_object.set('status', 'EDITING')
        base_object.set('lastChangedBy', self.username)
        base_object.set('checkedOutBy', self.username)
        base_object.set('version', '1.001')
        
        # Set dates
        now = datetime.now()
        formatted_date = now.strftime('%d/%m/%Y %H:%M:%S.%f')
        base_object.set('createDate', formatted_date)
        base_object.set('lastChangedDate', formatted_date)
        base_object.set('lastStatusChangedDate', formatted_date)
        base_object.set('effectivityDate', formatted_date)
        
        if attributes:
            for attrib_id, s_value in attributes.items():
                for a, s in ast.literal_eval(s_value).items():
                    attrib_id = a
                    s_value = s
                # Find the attribute by attribId
                attr = base_object.find(f".//eObjectAttribute[@attribId='{attrib_id}']")
                if attr is not None:
                    for elem_id in ['Value', 'UOM', 'Status Value']:
                        elem = attr.find(f".//eObjectAttributeElement[@elemId='{elem_id}']")
                        if elem is not None:
                            pop_method_attr = elem.get('popMethodAttr', '')
                            if pop_method_attr:
                                choices = [choice.strip() for choice in pop_method_attr.split(';')]
                                if choices and s_value not in choices:
                                    matched = next((c for c in choices if c.lower() == s_value.lower()), None)
                                    if matched:
                                        s_value = matched
                                    else:
                                        logger.debug(f"Value '{s_value}' not found in choices for '{attrib_id}'. Available: {choices}. Using provided value anyway.")
                            
                            elem.set('sValue', s_value)
                            logger.debug(f"Set {attrib_id} -> {s_value}")
                            break
                    else:
                        logger.warning(f"Could not find element to set sValue for attribute '{attrib_id}'")
                else:
                    logger.warning(f"Attribute '{attrib_id}' not found in template")
        
        temp_xml_path = os.path.join(os.path.dirname(__file__), 'Material_temp.xml')
        template.write(temp_xml_path, encoding='utf-8', xml_declaration=False)
        logger.debug(f"Modified template saved to: {temp_xml_path}")
        
        return temp_xml_path

    def create_template(
        self,
        material_id: str,
        material_description: Optional[str | None],
        attributes: Optional[dict] = None,
        template_name: str = "material_template.xml",
        pull: bool = False
    ) -> str | bool:
        """
        Creates a material XML file, optionally uploads and imports it.

        Args:
            material_id (str): ID for the material.
            material_description (str): Description for the material.
            attributes (dict): Dictionary mapping attribId to sValue.
            template_name (str): Name of the template XML file (default: "material_template.xml").
            pull (bool): If True, only creates the XML file and returns the path. If False, uploads and imports.

        Returns:
            str | bool: If pull=True, returns the path to the created XML file. If pull=False, returns True on success.
        """
        try:
            xml_file_path = self._modify_template_xml(
                material_id=material_id,
                material_description=material_description,
                attributes=attributes or {}
            )
            
            if pull:
                return xml_file_path
            
            if not self._perform_login():
                logger.error("Login failed. Cannot proceed with upload and import.")
                return False

            uploaded_file_uid, temp_server_filename = self._upload_file(xml_file_path)
            if not uploaded_file_uid:
                logger.error("File upload failed.")
                return False

            if not self._import_file(uploaded_file_uid, temp_server_filename):
                logger.error("File import failed.")
                return False
            
            logger.debug(f"Material '{material_id}' created and imported successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Error creating material: {e}", exc_info=True)
            return False

    def _upload_file(self, xml_file_path: str) -> tuple[Optional[str], Optional[str]]:
        """
        Uploads a single XML file to the server.

        Args:
            xml_file_path (str): Path to the XML file.
            xml_file_name (str): Name of the XML file.
            total_file_size (int): Size of the XML file in bytes.

        Returns:
            tuple: (uploaded_file_uid, temp_server_filename) or (None, None) on failure.
        """
        logger.debug(f"Initiating single file upload for '{xml_file_path}' to {self.file_upload_url}...")

        uploaded_file_uid = str(uuid.uuid4())
        total_file_size = os.path.getsize(xml_file_path)
        temp_server_filename = None

        try:
            with open(xml_file_path, 'rb') as f:
                full_file_content = f.read()

                metadata = {
                    "chunkIndex": 0,
                    "contentType": "text/xml",
                    "fileName": os.path.basename(xml_file_path),
                    "relativePath": os.path.basename(xml_file_path),
                    "totalFileSize": total_file_size,
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
                    'Host': self.machine_name,
                    'Origin': self.login_host,
                    'Referer': f"{self.base_app_url}SpecificationManagement.aspx",
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                }

                logger.debug(f"Uploading entire file as a single chunk (UID: {uploaded_file_uid})...")
                upload_response = self.session.post(self.file_upload_url, files=upload_files, headers=upload_headers, verify=False)
                upload_response.raise_for_status()

                upload_result = upload_response.json()
                logger.debug(f"Single upload response: {upload_result}")

                if upload_result.get("uploaded", False):
                    logger.debug("File uploaded successfully to server temp directory!")
                    temp_server_filename = upload_result.get("TempFileName")
                    uploaded_file_uid = upload_result.get("fileUid")
                    if uploaded_file_uid is None:
                        logger.warning("'fileUid' was not returned in the upload response. This might cause issues.")
                else:
                    logger.error(f"File failed to upload. Response: {upload_result}")
                    return None, None

            if not temp_server_filename:
                logger.error("File upload completed but no TempFileName was received from the server.")
                return None, None

            logger.debug(f"Full file uploaded successfully. Server temporary path: {temp_server_filename}")
            return uploaded_file_uid, temp_server_filename

        except requests.exceptions.RequestException as e:
            logger.error(f"File upload request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Status Code: {e.response.status_code}, Content: {e.response.text}")
            return None, None
        except Exception as e:
            logger.error(f"An unexpected error occurred during file upload: {e}")
            return None, None

    def _import_file(self, uploaded_file_uid: str, xml_file_name: str) -> Optional[dict]:
        """
        Calls the server's ImportFiles endpoint to import the uploaded XML file.

        Args:
            uploaded_file_uid (str): The UID of the uploaded file.
            xml_file_name (str): The original name of the XML file.
            obj_type (str): Object type extracted from XML.
            level_id (str): Level ID extracted from XML.
            location_id (str): Location ID extracted from XML.
            file_size (int): Size of the XML file.

        Returns:
            dict: The JSON response from the import API call, or None on failure.
        """
        logger.debug(f"Attempting to call ImportFiles with uploaded file UID: {uploaded_file_uid}...")

        file_size = os.path.getsize(os.path.join(os.path.dirname(__file__), 'Material_temp.xml'))

        file_entry = {
            "FileName": xml_file_name,
            "Extension": os.path.splitext(xml_file_name)[1],
            "Size": file_size,
            "Uid": uploaded_file_uid
        }

        pass_data_json = {
            "userID": self.username,
            "TreeIdentifier":"33499dad-a760-44e0-a3c5-49ce14f184c4",
            "Domain":"",
            "DLL":"POMS_ProcObject_Lib",
            "Type": "ConfiguredObject",
            "SubType":"MM_OBJ",
            "Level": self.level_id,
            "Location": self.location_id,
            "Folder":"",
            "SearchSubType":"",
            "Files":[file_entry],
            "Signature":{
                "SignatureRequired":False,
                "UserID": self.username,
                "UserName": self.username,
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
            'Origin': self.login_host,
            'Referer': f"{self.base_app_url}SpecificationManagement.aspx",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }

        try:
            response = self.session.post(self.import_url, json=pass_data_json, headers=headers_for_import, verify=False)
            response.raise_for_status()

            result = response.json()
            logger.info("Import request successful!")
            logger.debug(f"Response JSON: {json.dumps(result, indent=2)}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Import request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Status Code: {e.response.status_code}, Content: {e.response.text}")
            return None
