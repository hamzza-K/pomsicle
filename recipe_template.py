
import requests
import json
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timezone
from credentials import login


from config import config

settings = config(translator='pomsicle')

USERNAME = settings['USERNAME']
PASSWORD = settings['PASSWORD']

print("Checking credentials...")
token = login(username=USERNAME, password=PASSWORD)

# --- XML File Processing ---
xml_folder = "data"
xml_file_name = "Recipe_Scratch_Vial_1.001_2024_Oct_22_06_30_40.xml" # This should match your actual file name
xml_file_path = os.path.join(xml_folder, xml_file_name)

# Ensure the 'data' folder exists and the XML file is there
if not os.path.exists(xml_file_path):
    print(f"Error: XML file not found at '{xml_file_path}'. Please ensure the 'data' folder exists and contains the XML file.")
    exit()

# Extract information from the XML
try:
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    # Assuming the first 'eProcObject' contains the relevant data
    e_proc_object = root.find(".//eProcObject")

    if e_proc_object is None:
        print("Error: Could not find 'eProcObject' element in the XML file.")
        exit()

    # Retrieve attributes
    obj_type = e_proc_object.get("objType")
    level_id = e_proc_object.get("levelId")
    location_id = e_proc_object.get("locationId")
    version = e_proc_object.get("version")
    guid = e_proc_object.get("guid")

    # You might need to determine the file size dynamically if it changes
    file_size = os.path.getsize(xml_file_path)

    # Construct the file entry for the payload
    file_entry = {
        "FileName": xml_file_name,
        "Extension": os.path.splitext(xml_file_name)[1],
        "Size": file_size,
        "Uid": guid # Using the GUID from the XML as Uid
    }

except FileNotFoundError:
    print(f"Error: The file '{xml_file_path}' was not found.")
    exit()
except ET.ParseError as e:
    print(f"Error parsing XML file: {e}")
    exit()
except Exception as e:
    print(f"An unexpected error occurred during XML processing: {e}")
    exit()

# --- POST Request Setup ---
url = "http://win-bkblmqnn8d9/poms/apps/eSpecWebApplication/SpecificationManagement.aspx/ImportFiles"

pass_data = {
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
        "UserID2":"",
        "UserName2":"",
        "Comment":""
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

# Set the headers for the request
headers = {
    "Content-Type": "application/json;charset=utf-8"
}

# --- Send POST Request ---
try:
    response = requests.post(url, json=pass_data, headers=headers)

    response.raise_for_status()

    result = response.json()
    print("Request successful!")
    print("Response JSON:")
    print(json.dumps(result, indent=2))

except requests.exceptions.HTTPError as errh:
    print(f"HTTP Error: {errh}")
    print(f"Response content: {response.text}")
except requests.exceptions.ConnectionError as errc:
    print(f"Error Connecting: {errc}")
except requests.exceptions.Timeout as errt:
    print(f"Timeout Error: {errt}")
except requests.exceptions.RequestException as err:
    print(f"An unexpected error occurred: {err}")