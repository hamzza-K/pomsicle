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

logger = logging.getLogger(__name__)

class PomsicleTemplateManager:
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
        self._is_logged_in = False  # Track login state

    def _perform_login(self) -> bool:
        """
        Performs a browser-like login to the POMSicle system.
        Only performs login if not already logged in.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        # Skip if already logged in
        if self._is_logged_in:
            logger.debug("Already logged in, skipping login.")
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
            logger.debug(f"XML parsed successfully. objType: {obj_type}, levelId: {level_id}, locationId: {location_id}")
            return obj_type, level_id, location_id, file_size

        except (FileNotFoundError, ET.ParseError, Exception) as e:
            logger.error(f"Error during XML processing: {e}")
            return None, None, None, None

    def _modify_template_xml(self, xml_file_path: str, recipe_name: str = None, unit_procedure_name: str = None, operation_name: str = None) -> bool:
        """
        Modifies the 'id' attributes of <eProcObject> and <eProcCompObject> tags
        in the XML template based on provided names and objType.
        Also updates 'displayText' in objectConfig for eProcCompObject.

        Args:
            xml_file_path (str): Path to the XML file to modify.
            recipe_name (str, optional): New name for PM_RECIPE. Defaults to None.
            unit_procedure_name (str, optional): New name for PM_SUP. Defaults to None.
            operation_name (str, optional): New name for PM_OPERATION. Defaults to None.

        Returns:
            bool: True if modification was successful, False otherwise.
        """
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            # Mapping of objType to provided names
            name_map = {
                "PM_RECIPE": recipe_name,
                "PM_SUP": unit_procedure_name or recipe_name,
                "PM_OPERATION": operation_name or recipe_name
            }

            # Update eProcObject tags
            for obj in root.findall(".//eProcObject"):
                obj_type = obj.get("objType")
                new_id = name_map.get(obj_type)
                if new_id:
                    original_id = obj.get("id")
                    obj.set("id", new_id)
                    logger.debug(f"Updated eProcObject 'id' from '{original_id}' to '{new_id}' for objType='{obj_type}'.")
                    # Also update description if it contains "Template" and matches objType pattern
                    description = obj.get("description", "")
                    if "Template" in description:
                         # Simple replacement if description contains "Template"
                        obj.set("description", description.replace("Template", new_id))
                        logger.debug(f"Updated eProcObject 'description' for '{new_id}'.")


            # Update eProcCompObject tags (nested components)
            # These also have 'compProcType' and 'compObjId' attributes, and 'displayText' in objectConfig
            for comp_obj in root.findall(".//eProcCompObject"):
                comp_proc_type = comp_obj.get("compProcType")
                new_id = name_map.get(comp_proc_type)
                if new_id:
                    original_comp_obj_id = comp_obj.get("compObjId")

                    comp_obj.set("compObjId", new_id)
                    logger.debug(f"Updated eProcCompObject 'compObjId' from '{original_comp_obj_id}' to '{new_id}' for compProcType='{comp_proc_type}'.")
                    
                    # Update 'displayText' within the 'objectConfig' JSON string if present
                    object_config_str = comp_obj.get("objectConfig")
                    if object_config_str:
                        try:
                            object_config = json.loads(object_config_str)
                            # Update label.text for older versions or if the label element is directly the text
                            if 'Label' in object_config and 'text' in object_config['Label']:
                                object_config['Label']['text'] = new_id
                            # For newer versions or if the Label element is more complex
                            if 'Label' in object_config and 'styles' in object_config['Label'] and 'text' not in object_config['Label']:
                                # Some templates might store text directly in objectConfig or not expose it.
                                # This is a common place for the displayed text.
                                object_config['Label']['text'] = new_id
                            
                            # If displayText is explicitly mapped, it might also be here
                            # This part is highly dependent on exact XML structure and what POMSicle reads
                            if 'displayText' in object_config:
                                object_config['displayText'] = new_id

                            comp_obj.set("objectConfig", json.dumps(object_config))
                            logger.debug(f"Updated 'displayText' in objectConfig for '{new_id}'.")
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse objectConfig JSON for {comp_proc_type} with ID '{original_comp_obj_id}'. Skipping config update.")


            tree.write(xml_file_path, encoding="UTF-8", xml_declaration=False)
            logger.info(f"XML file '{xml_file_path}' modified successfully with new names.")
            return True
        except ET.ParseError as e:
            logger.error(f"Error parsing XML file '{xml_file_path}': {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during XML modification: {e}")
            return False

    def _upload_file(self, xml_file_path: str, xml_file_name: str, total_file_size: int):
        """
        Uploads a single XML file to the server.

        Args:
            xml_file_path (str): Path to the XML file.
            xml_file_name (str): Name of the XML file.
            total_file_size (int): Size of the XML file in bytes.

        Returns:
            tuple: (uploaded_file_uid, temp_server_filename) or (None, None) on failure.
        """
        logger.debug(f"Initiating single file upload for '{xml_file_name}' to {self.file_upload_url}...")

        uploaded_file_uid = str(uuid.uuid4())
        temp_server_filename = None

        try:
            with open(xml_file_path, 'rb') as f:
                full_file_content = f.read()

                metadata = {
                    "chunkIndex": 0,
                    "contentType": "text/xml",
                    "fileName": xml_file_name,
                    "relativePath": xml_file_name,
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
                    'Referer': f"{self.base_app_url}/SpecificationManagement.aspx",
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

    def _import_file(self, uploaded_file_uid: str, xml_file_name: str, obj_type: str, level_id: str, location_id: str, file_size: int):
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

        file_entry = {
            "FileName": xml_file_name,
            "Extension": os.path.splitext(xml_file_name)[1],
            "Size": file_size,
            "Uid": uploaded_file_uid
        }

        pass_data_json = {
            "userID": self.username,
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

    def create_template(self, template_name: str = "Template.xml", recipe_name: str = None, unit_procedure_name: str = None, operation_name: str = None):
        """
        Main method to create a template by uploading and importing an XML file.
        Modifies the XML template with provided names before upload.

        Args:
            template_name (str): The name of the template XML file to use.
                                 (Assumed to be in the 'data' folder relative to script)
            recipe_name (str, optional): New name for PM_RECIPE. Defaults to None.
            unit_procedure_name (str, optional): New name for PM_SUP. Defaults to None.
            operation_name (str, optional): New name for PM_OPERATION. Defaults to None.
        """
        logger.info(f"Attempting to create recipe: '{template_name}'")

        if not self._perform_login():
            logger.critical("Login failed. Cannot proceed with template creation.")
            return False

        xml_folder = os.path.join(self.program_path, 'template')
        xml_file_path = os.path.join(xml_folder, template_name)

        temp_xml_file_path = f"{xml_file_path}.temp_{uuid.uuid4().hex}"
        try:
            import shutil
            shutil.copy(xml_file_path, temp_xml_file_path)
            logger.debug(f"Created temporary XML file for modification: {temp_xml_file_path}")
        except Exception as e:
            logger.error(f"Failed to create temporary XML file: {e}")
            return False

        # --- XML Modification Step ---
        if recipe_name or unit_procedure_name or operation_name:
            logger.debug("Modifying XML template with provided names...")
            if not self._modify_template_xml(temp_xml_file_path, recipe_name, unit_procedure_name, operation_name):
                logger.error("Failed to modify XML template. Aborting.")
                os.remove(temp_xml_file_path)
                return False
        else:
            logger.info("No specific names provided for template modification. Using original IDs.")


        obj_type, level_id, location_id, file_size = self._process_xml_file(temp_xml_file_path)
        if not all([obj_type, level_id, location_id, file_size]):
            logger.error("Failed to process XML file for template creation. Aborting.")
            os.remove(temp_xml_file_path)
            return False

        uploaded_file_uid, temp_server_filename = self._upload_file(temp_xml_file_path, template_name, file_size)
        
        try:
            if os.path.exists(temp_xml_file_path):
                os.remove(temp_xml_file_path)
                logger.debug(f"Cleaned up temporary XML file: {temp_xml_file_path}")
        except OSError as e:
            logger.warning(f"Failed to delete temporary XML file '{temp_xml_file_path}': {e}")


        if not uploaded_file_uid:
            logger.error("File upload failed. Aborting template creation.")
            return False

        import_result = self._import_file(uploaded_file_uid, template_name, obj_type, level_id, location_id, file_size)

        if import_result and import_result.get("d", {}).get("Success"):
            logger.debug(f"Template '{template_name}' imported successfully.")
            Banner().success(f"Recipe '{recipe_name or template_name}' created successfully.")
            return True
        else:
            logger.error(f"Template '{template_name}' import was not successful.")
            Banner.error(f"Template '{template_name}' import was not successful.")
            return False