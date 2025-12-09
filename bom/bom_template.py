import requests
import json
import xml.etree.ElementTree as ET
import os
import logging
import copy
from datetime import datetime, timezone
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from banners import Banner
import uuid

logger = logging.getLogger(__name__)

class PomsicleBOMManager:
    """
    Manages the upload and import of BOM XML files to POMSicle.
    """
    def __init__(self, settings: dict, bom_settings: dict, materials: list, username: str, password: str):
        """
        Initializes the PomsicleBOMManager with configuration settings and credentials.

        Args:
            settings (dict): A dictionary containing POMSicle configuration details
                             (e.g., MACHINE_NAME, BASE_APP_URL).
            materials (list): A list of materials to include in the BOM.
            username (str): The username for POMSicle login.
            password (str): The password for POMSicle login.
        """
        self.settings = settings
        self.username = username
        self.password = password
        self.materials = materials
        
        self.base_app_url = settings.get('BASE_APP_URL')
        self.import_url = settings.get('IMPORT_URL')
        self.file_upload_url = settings.get('FILE_UPLOAD_URL')
        self.login_host = settings.get('LOGIN_HOST')
        self.machine_name = settings.get('MACHINE_NAME')
        self.program_path = settings.get('PROGRAM_BASE_PATH')
        self.materials_url = settings.get('MATERIALS_URL')

        self.level_id = bom_settings.get('LEVEL_ID', '10')
        self.location_id = bom_settings.get('LOCATION_ID', '4')
        self.location_name = bom_settings.get('LOCATION_NAME', 'Herndon')

        self.session = requests.Session()
        
        self.file_upload_url = self.login_host + '/' + self.base_app_url + '/' + self.file_upload_url
        self.import_url = self.login_host + '/' + self.base_app_url + '/' + self.import_url

        self.login_page_relative_path = "/POMS/DesktopDefault.aspx"
        self.espec_model_base_path = "/poms/apps/eSpecWebApplication/"
        self.espec_model_base_poms_path = "/poms/"

        self.materials_api = self.login_host + '/' + self.materials_url

        self.configuredObject_objType = "MM_OBJ"

        self.fetched_materials = self._get_materials()

        if not all([self.username, self.password, self.machine_name, self.base_app_url,
                    self.import_url, self.file_upload_url, self.login_host]):
            logger.critical("Missing essential configuration variables in settings. Exiting.")
            raise ValueError("Missing essential configuration variables for PomsicleTemplateManager.")
        
    def _get_materials(self) -> dict:
        """
        Fetches material details from the POMS materials API.

        Returns:
            dict: A dictionary of material details keyed by material ID.
        """
        materials_data = {}
        for material_id in self.materials:
            material_url = f"{self.materials_api}/{material_id}"
            try:
                logger.debug(f"Fetching material data from: {material_url}")
                response = self.session.get(material_url, verify=False)
                response.raise_for_status()
                material_info = response.json()
                if 'MATERIAL_ID' not in material_info.keys():
                    logger.warning(f"Material '{material_id}' not found in system.")
                    continue
                materials_data[material_id] = material_info
                logger.debug(f"Material data retrieved: {material_info}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch material '{material_id}': {e}")
        return materials_data


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
                obj_type = self.configuredObject_objType
                level_id = self.level_id
                location_id = self.location_id
            else:
                obj_type = e_proc_object.get("objType")
                level_id = e_proc_object.get("levelId")
                location_id = e_proc_object.get("locationId")
            logger.debug(f"XML parsed successfully. objType: {obj_type}, levelId: {level_id}, locationId: {location_id}")
            return obj_type, level_id, location_id, file_size

        except (FileNotFoundError, ET.ParseError, Exception) as e:
            logger.error(f"Error during XML processing: {e}")
            return None, None, None, None

    def _modify_template_xml(self, bom_name: str = None) -> str:
        """
        Modifies the template XML by stitching together header, line items, and base objects.
        Uses deep copies to ensure original template files are never modified.
        
        Args:
            bom_name (str): Name for the BOM. If None, generates a UUID-based name.
            
        Returns:
            str: Path to the modified XML file.
        """
        # Parse template files - these are read-only and will never be modified
        # We create deep copies of all elements before making any changes
        template = ET.parse(os.path.join(os.path.dirname(__file__), 'template', 'template.xml'))
        header_tree = ET.parse(os.path.join(os.path.dirname(__file__), 'objects', 'header.xml'))
        line_item_tree = ET.parse(os.path.join(os.path.dirname(__file__), 'objects', 'line_item.xml'))
        base_tree = ET.parse(os.path.join(os.path.dirname(__file__), 'objects', 'base.xml'))
        
        # Get template structure - this will be modified to build the output file
        # but the original template.xml file on disk remains unchanged
        template_root = template.getroot()
        e_spec_xml_objs = template_root.find('eSpecXmlObjs')
        
        # Create a deep copy of the header to avoid modifying the original template file
        # Using ET.fromstring(ET.tostring(...)) creates a completely independent copy
        header = ET.fromstring(ET.tostring(header_tree.getroot(), encoding='unicode'))
        header.set('id', bom_name or 'POMSICLE_BOM_' + str(uuid.uuid4()))
        header.set('locationId', self.location_id)
        header.set('levelId', self.level_id)
        header.set('locationName', self.location_name)
        
        # Add line items for each material inside the header
        item_number = 1
        for material_id, material_info in self.fetched_materials.items():
            # Create a deep copy of the line item template to avoid modifying the original file
            # Using ET.fromstring(ET.tostring(...)) creates a completely independent copy
            line_item = ET.fromstring(ET.tostring(line_item_tree.getroot(), encoding='unicode'))
            
            # Set line item attributes
            line_item.set('itemLevelName', 'Master')
            line_item.set('itemLevelId', self.level_id)
            line_item.set('itemLocName', self.location_name)
            line_item.set('itemLocId', self.location_id)
            line_item.set('itemObjId', material_id)
            line_item.set('itemObjTypeName', 'MM_OBJ')
            line_item.set('parentRule', 'Percent')
            line_item.set('itemNumber', str(item_number))
            line_item.set('subNumber', '1')
            line_item.set('seqNumber', str(item_number))
            line_item.set('itemObjType', '2')
            line_item.set('itemObjVer', '1.001')
            line_item.set('activeFlag', 'True')
            line_item.set('aggregateFlag', 'True')
            
            # Modify sValue in Dispense UOM element (if material has INVENTORY_UOM)
            inventory_uom = material_info.get('INVENTORY_UOM', '#')
            dispense_attr = line_item.find(".//eObjectAttribute[@attribId='Dispense']")
            if dispense_attr is not None:
                uom_elem = dispense_attr.find(".//eObjectAttributeElement[@elemId='UOM']")
                if uom_elem is not None:
                    uom_elem.set('sValue', inventory_uom if inventory_uom else '#')
            
            # Append line item to header
            header.append(line_item)
            item_number += 1
        
        # Append header to template
        e_spec_xml_objs.append(header)
        
        # Add base objects for each material
        for material_id, material_info in self.fetched_materials.items():
            # Create a deep copy of the base template to avoid modifying the original file
            # Using ET.fromstring(ET.tostring(...)) creates a completely independent copy
            base = ET.fromstring(ET.tostring(base_tree.getroot(), encoding='unicode'))
            
            # Set base object attributes
            base.set('objType', 'MM_OBJ')
            base.set('relObjType', 'MM')
            base.set('id', material_id)
            base.set('levelName', 'Master')
            base.set('levelId', self.level_id)
            base.set('locationName', self.location_name)
            base.set('locationId', self.location_id)
            
            # Set description from material info
            material_desc = material_info.get('MATERIAL_DESC', '')
            base.set('description', material_desc)
            
            # Set status and version
            base.set('status', 'APPROVED')
            base.set('version', '1.001')
            
            # Convert and set lastChangedDate
            last_changed_date = material_info.get('LAST_CHANGED_DATE', '')
            if last_changed_date:
                try:
                    # Parse ISO format: '2025-09-17T05:30:30.18407' or '2025-09-17T05:30:30.18407Z'
                    date_str = last_changed_date.replace('Z', '+00:00')
                    if '+' not in date_str and date_str.count('-') >= 2:
                        # No timezone info, assume UTC
                        if 'T' in date_str:
                            date_str = date_str + '+00:00'
                    dt = datetime.fromisoformat(date_str)
                    # Convert to UTC if timezone-aware
                    if dt.tzinfo:
                        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                    # Format as: '17/09/2025 05:30:30.184815'
                    formatted_date = dt.strftime('%d/%m/%Y %H:%M:%S.%f')
                    base.set('lastChangedDate', formatted_date)
                    base.set('createDate', formatted_date)
                    base.set('lastStatusChangedDate', formatted_date)
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Could not parse date '{last_changed_date}': {e}")
                    # Use current date as fallback
                    now = datetime.now()
                    formatted_date = now.strftime('%d/%m/%Y %H:%M:%S.%f')
                    base.set('lastChangedDate', formatted_date)
                    base.set('createDate', formatted_date)
                    base.set('lastStatusChangedDate', formatted_date)
            else:
                # Use current date if no date provided
                now = datetime.now()
                formatted_date = now.strftime('%d/%m/%Y %H:%M:%S.%f')
                base.set('lastChangedDate', formatted_date)
                base.set('createDate', formatted_date)
                base.set('lastStatusChangedDate', formatted_date)
            
            base.set('lastChangedBy', self.username)
            
            # Modify base object attributes based on material info
            # Default Quality Status Value
            default_qc_status = material_info.get('DEFAULT_QC_STATUS', 'Released')
            default_quality_attr = base.find(".//eObjectAttribute[@attribId='Default Quality']")
            if default_quality_attr is not None:
                status_elem = default_quality_attr.find(".//eObjectAttributeElement[@elemId='Status Value']")
                if status_elem is not None:
                    status_elem.set('sValue', default_qc_status)
            
            # Inventory Tracking
            inventory_tracking = material_info.get('INVENTORY_TRACKING', 'Container')
            inventory_tracking_attr = base.find(".//eObjectAttribute[@attribId='Inventory Tracking']")
            if inventory_tracking_attr is not None:
                tracking_elem = inventory_tracking_attr.find(".//eObjectAttributeElement[@elemId='Value']")
                if tracking_elem is not None:
                    tracking_elem.set('sValue', inventory_tracking)
            
            # Inventory UOM
            inventory_uom = material_info.get('INVENTORY_UOM', 'g')
            inventory_uom_attr = base.find(".//eObjectAttribute[@attribId='Inventory UOM']")
            if inventory_uom_attr is not None:
                uom_elem = inventory_uom_attr.find(".//eObjectAttributeElement[@elemId='UOM']")
                if uom_elem is not None:
                    uom_elem.set('sValue', inventory_uom)
            
            # Storage Class
            storage_class = material_info.get('STORAGE_CLASS', 'AMBIENT')
            storage_class_attr = base.find(".//eObjectAttribute[@attribId='Storage Class']")
            if storage_class_attr is not None:
                storage_elem = storage_class_attr.find(".//eObjectAttributeElement[@elemId='Value']")
                if storage_elem is not None:
                    storage_elem.set('sValue', storage_class)
            
            # Append base to template
            e_spec_xml_objs.append(base)
        
        # Save the modified template to a temporary file
        temp_xml_path = os.path.join(os.path.dirname(__file__), 'Bom_temp.xml')
        template.write(temp_xml_path, encoding='utf-8', xml_declaration=True)
        logger.debug(f"Modified template saved to: {temp_xml_path}")
        
        return temp_xml_path

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
            "TreeIdentifier":"33499dad-a760-44e0-a3c5-49ce14f184c4",
            "Domain":"",
            "DLL":"POMS_ProcObject_Lib",
            "Type": obj_type,
            "SubType":"MM_BOM",
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

    def create_template(self, template_name: str = "Bom_template.xml", bom_name: str = None):
        """
        Main method to create a template by uploading and importing an XML file.
        Modifies the XML template with provided names before upload.

        Args:
            template_name (str): The name of the template XML file to use.
            bom_name (str): Name for the BOM. If None, generates a UUID-based name.
        """
        logger.info(f"Attempting to create BOM: '{bom_name}'")

        if not self._perform_login():
            logger.critical("Login failed. Cannot proceed with template creation.")
            return False

        # Generate the modified template XML
        logger.debug("Modifying XML template with materials and BOM name...")
        try:
            temp_xml_file_path = self._modify_template_xml(bom_name)
            if not temp_xml_file_path or not os.path.exists(temp_xml_file_path):
                logger.error("Failed to generate modified XML template. Aborting.")
                return False
        except Exception as e:
            logger.error(f"Failed to modify XML template: {e}")
            return False

        file_size = os.path.getsize(temp_xml_file_path)

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

        import_result = self._import_file(uploaded_file_uid, template_name, self.configuredObject_objType, self.level_id, self.location_id, file_size)

        if import_result and import_result.get("d", {}).get("Success"):
            logger.debug(f"Template '{template_name}' imported successfully.")
            Banner().success(f"BOM '{bom_name or template_name}' created successfully.")
            return True
        else:
            logger.error(f"Template '{template_name}' import was not successful.")
            Banner.error(f"Template '{template_name}' import was not successful.")
            return False