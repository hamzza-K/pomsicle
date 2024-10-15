import os
import requests
import configparser
import xml.etree.ElementTree as ET

config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), '../config/config.cfg')
config.read(config_file)
settings = config['pomsicle']


# Weird Namespacing restrictions when sending the data in .xml format.

NAMESPACE = "http://schemas.datacontract.org/2004/07/Poms.WebAPI.Models"
MACHINE_NAME = settings["MACHINE_NAME"]
BASE_URL = f'http://{MACHINE_NAME}/poms-api/'
TRANSLATOR_INSTANCE_ID = settings["TRANSLATOR_INSTANCE_ID"]
DEFAULT_MEDIA_TYPE = "application/json"

# ET.register_namespace("", NAMESPACE)

# def build_transaction_data_model(instance_id: str, transaction_id: str, transaction_value_xml: str) -> str:
#     """Builds the XML payload with the TransactionValue as an escaped string."""
#     # Create the root element with namespace
#     root = ET.Element(f"{{{NAMESPACE}}}TransactionDataModel")

#     # Add child elements
#     ET.SubElement(root, "InstanceID").text = instance_id
#     ET.SubElement(root, "TransactionID").text = transaction_id

#     # Add TransactionValue as escaped XML content
#     transaction_value_element = ET.SubElement(root, "TransactionValue")
#     transaction_value_element.text = ET.tostring(
#         ET.fromstring(transaction_value_xml), encoding="unicode"
#     )

#     # Convert XML tree to string with declaration
#     return ET.tostring(root, encoding="UTF-8", xml_declaration=True).decode("UTF-8")

def call(token: str, material_file: str):
    path = BASE_URL + "v1/Interface/Transaction/Call"

    headers = {"Content-Type": DEFAULT_MEDIA_TYPE, "Authorization": f"Bearer {token}"}

    payload = {
        "InstanceID": TRANSLATOR_INSTANCE_ID,
        "TransactionID": "*",
        "TransactionValue": material_file,
    }


    print("Request Payload::", payload)

    response = requests.post(path, data=payload, headers=headers, timeout=10)

    if response.status_code == 200:
        return response.text
    else:
        return response, response.text


# def call(token: str, transaction_value_xml: str):
    """Sends the XML request to the API."""
    path = BASE_URL + "v1/Interface/Transaction/Call"
    headers = {"Content-Type": DEFAULT_MEDIA_TYPE, "Authorization": f"Bearer {token}"}

    # Build the XML payload
    xml_payload = build_transaction_data_model(
        instance_id="pomsicle",
        transaction_id="*",
        transaction_value_xml=transaction_value_xml
    )

    print("Request Payload::", xml_payload)  # Verify the output

    # Make the POST request
    response = requests.post(path, data=xml_payload, headers=headers, timeout=20)

    if response.status_code == 200:
        return response.text
    else:
        return response, response.text
