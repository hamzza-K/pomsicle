import json
import xml.etree.ElementTree as ET


"""This creates the structure of Materials in XML or JSON formats."""
# ========================= Class ========================
class POMSTransactionXML:
    def __init__(self):
        self.root   = ET.Element("POMSTransaction")
        self.header = ET.SubElement(self.root, "Header")
        self.record = ET.SubElement(self.root, "Record")

    def add_header(self, name: str, text: str) -> None:
        ET.SubElement(self.header, name).text = text

    def add_record(self, name: str, text: str) -> None:
        ET.SubElement(self.record, name).text = text

    def add_records(self, records):
        for record in records:
            self.add_record(*record)

    def remove_header(self):
        for child in self.root.findall("Header"):
            self.root.remove(child)

    def remove_records(self):
        for child in self.root.findall("Record"):
            self.root.remove(child)

    def to_string(self):
        return ET.tostring(self.root, encoding="UTF-8", xml_declaration=True)

    def save(self, file_name: str = "MasterMaterial.xml"):
        tree = ET.ElementTree(self.root)
        tree.write(file_name, encoding="UTF-8", xml_declaration=True)


class POMSTransactionJSON:
    def __init__(self):
        self.data = {
            "POMSTransaction": {
                "Header": {},
                "Record": {}
            }
        }

    def add_header(self, name: str, text: str) -> None:
        self.data["POMSTransaction"]["Header"][name] = text

    def add_record(self, name: str, text: str) -> None:
        self.data["POMSTransaction"]["Record"][name] = text

    def add_records(self, records):
        for record in records:
            self.add_record(*record)

    def remove_header(self):
        self.data["POMSTransaction"]["Header"] = {}

    def remove_record(self):
        self.data["POMSTransaction"]["Record"] = []

    def to_string(self):
        return json.dumps(self.data, indent=4)
    
    def save(self, file_name: str = "MaterialMaster.json"):
        with open(file_name, 'w') as f:
            json.dump(self.data, f, indent=4)
    
