import xml.etree.ElementTree as ET
import secrets
from datetime import datetime
from typing import Optional, List, Tuple
import json

class Inventory:
    def __init__(self):
        self.root = ET.Element("POMSTransaction")
        self.header = None
        self.record = None
        self.line = None

    def add_header(self, name: str, text: str) -> None:
        if self.header is None:
            self.header = ET.SubElement(self.root, "Header")
        ET.SubElement(self.header, name).text = text

    def add_record(self, name: str, text: str) -> None:
        if self.record is None:
            self.record = ET.SubElement(self.root, "Record")
        ET.SubElement(self.record, name).text = text

    def add_records(self, records):
        for record in records:
            self.add_record(*record)

    def remove_header(self):
        if self.header is not None:
            self.root.remove(self.header)
            self.header = None

    def remove_records(self):
        if self.record is not None:
            self.root.remove(self.record)
            self.record = None

    def to_string(self, xml_declaration: bool = True) -> str:
        # Convert the XML tree to a byte string
        byte_string = ET.tostring(self.root, encoding="UTF-8", xml_declaration=xml_declaration)
        # Decode the byte string to a normal string
        return byte_string.decode("UTF-8")

    def save(self, file_name: str = "inventory.xml", xml_declaration: bool = True):
        tree = ET.ElementTree(self.root)
        tree.write(file_name, encoding="UTF-8", xml_declaration=xml_declaration)




# ========================== Inventory JSON ========================#
class InventoryJSON:
    def __init__(self):
        self.data = {
            "POMSTransaction": {
                "Header": {},
                "Record": {}
            }
        }

    def add_header(self, name: str, text: str) -> None:
        """Adds a header key-value pair."""
        self.data["POMSTransaction"]["Header"][name] = text

    def add_record(self, name: str, text: str) -> None:
        """Adds a single record key-value pair."""
        self.data["POMSTransaction"]["Record"][name] = text

    def add_records(self, records: List[Tuple[str, str]]) -> None:
        """Adds multiple records from a list of tuples."""
        for name, text in records:
            self.add_record(name, text)

    def remove_header(self) -> None:
        """Removes the Header section."""
        self.data["POMSTransaction"]["Header"] = {}

    def remove_records(self) -> None:
        """Removes the Record section."""
        self.data["POMSTransaction"]["Record"] = {}

    def to_string(self, indent: Optional[int] = 4) -> str:
        """Returns the JSON data as a formatted string."""
        return json.dumps(self.data, indent=indent)

    def save(self, file_name: str = "bom.json", indent: Optional[int] = 4) -> None:
        """Saves the JSON data to a file."""
        with open(file_name, "w", encoding="UTF-8") as f:
            json.dump(self.data, f, indent=indent)
# ========================== Inventory Json ====================


# ========================== HEADER =======================
class Header:
    """Adds the header in the JSON or XML payloads. This is Optional."""
    def __init__(self):
        self._timestamp = None
        self._transaction_ref_id = None

    # @property
    # def TIMESTAMP(self):
    #     if self._timestamp is None:
    #         self._timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
           
    #     return self._timestamp

    # @property
    # def TRANSACTION_REF_ID(self):
    #     if self._transaction_ref_id is None:
    #         self._transaction_ref_id = secrets.token_hex(16)
    #     return self._transaction_ref_id
    
    # TIMESTAMP = datetime.now().isoformat()

    TIMESTAMP = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    TRANSACTION_REF_ID = secrets.token_hex(16)
    TRANSACTION_ID = "INVENTORY"
    SOURCE_SYSTEM = "Pomsicle"
    SOURCE_SITE_ID = "0001"
    TARGET_SYSTEM = "POMSnet"


# ========================= RECORD =======================
class Record:
    """Adds the records in the JSON or XML transaction payloads."""
    MATERIAL_ID = "100032"
    PLANT_ID = "Herndon"
    MATERIAL_QTY = "100"
    LOCATION_ID = "Freeze2"
    UOM = "kg"
    MATERIAL_TYPE = "Raw Material"
    CONTAINER_ID = "C-10204"
    LOT_ID = "L000000011"
    LOT_STATUS = "Released"
    AREA_ID = "Freezer"



def header_lookup(header: Header) -> dict:
    header_look_up = {
        "TransactionID": header.TRANSACTION_ID,
        "TransactionTimeStamp": header.TIMESTAMP,
        "TransactionRefID": header.TRANSACTION_REF_ID,
        "SourceSystem": header.SOURCE_SYSTEM,
        "SourceSiteID": header.SOURCE_SITE_ID,
        "TargetSystem": header.TARGET_SYSTEM
    }

    return header_look_up


def record_lookup(record: Record) -> dict:
    record_look_up = {
        "PLANTID": record.PLANT_ID,
        "MATERIALID": record.MATERIAL_ID,
        "MATERIAL_QTY": record.MATERIAL_QTY,
        "LOCATION_ID": record.LOCATION_ID,
        "UOM": record.UOM,
        "MATERIAL_TYPE": record.MATERIAL_TYPE,
        "CONTAINER_ID": record.CONTAINER_ID,
        "LOT_ID": record.LOT_ID,
        "LOT_STATUS": record.LOT_STATUS,
        "AREA_ID": record.AREA_ID
    }

    return record_look_up
