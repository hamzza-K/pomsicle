import xml.etree.ElementTree as ET
import secrets
from datetime import datetime

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

    def to_string(self, xml_declaration: bool = False) -> str:
        return ET.tostring(self.root, encoding="UTF-8", xml_declaration=xml_declaration)

    def save(self, file_name: str = "bom.xml", xml_declaration: bool = False):
        tree = ET.ElementTree(self.root)
        tree.write(file_name, encoding="UTF-8", xml_declaration=xml_declaration)


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
    SOURCE_SYSTEM = "Pomsicle: The inventory loader"
    SOURCE_SITE_ID = "0001"
    TARGET_SYSTEM = "POMSnet"


# ========================= RECORD =======================
class Record:
    """Adds the records in the JSON or XML transaction payloads."""
    MATERIAL_ID = "100031"
    PLANT_ID = "Herndon"
    MATERIAL_QTY = "100"
    LOCATION_ID = "Freeze1"
    UOM = "kg"
    MATERIAL_TYPE = "Raw Material"
    CONTAINER_ID = "C-10203"
    LOT_ID = "L000000011"
    LOT_STATUS = "Released"
    AREA_ID = "Freezer"



def header_lookup(header: Header) -> dict:
    header_look_up = {
        "TransactionID": Header.TRANSACTION_ID,
        "TransactionTimeStamp": Header.TIMESTAMP,
        "TransactionRefID": Header.TRANSACTION_REF_ID,
        "SourceSystem": Header.SOURCE_SYSTEM,
        "SourceSiteID": Header.SOURCE_SITE_ID,
        "TargetSystem": Header.TARGET_SYSTEM
    }

    return header_look_up


def record_lookup(record: Record) -> dict:
    record_look_up = {
        "PLANTID": Record.PLANT_ID,
        "MATERIALID": Record.MATERIAL_ID,
        "MATERIAL_QTY": Record.MATERIAL_QTY,
        "LOCATION_ID": Record.LOCATION_ID,
        "UOM": Record.UOM,
        "MATERIAL_TYPE": Record.MATERIAL_TYPE,
        "CONTAINER_ID": Record.CONTAINER_ID,
        "LOT_ID": Record.LOT_ID,
        "LOT_STATUS": Record.LOT_STATUS,
        "AREA_ID": Record.AREA_ID
    }

    return record_look_up
