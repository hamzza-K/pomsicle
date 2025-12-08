import xml.etree.ElementTree as ET

class BOM_XML:
    def __init__(self):
        self.root = ET.Element("POMSTransaction")
        self.header = None
        self.record = None
        self.line   = None

    def add_header(self, name: str, text: str) -> None:
        if self.header is None:
            self.header = ET.SubElement(self.root, "Header")
        ET.SubElement(self.header, name).text = text

    def add_record(self, name: str, text: str) -> None:
        if self.record is None:
            self.record = ET.SubElement(self.root, "Record")
        ET.SubElement(self.record, name).text = text

    def add_line_item(self, name: str, text: str) -> None:
        if self.record is None:
            raise ValueError("Cannot add line item without a record.")
        if self.line is None:
            self.line = ET.SubElement(self.record, "LineItem")
        ET.SubElement(self.line, name).text = str(text)

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

    def to_string(self):
        return ET.tostring(self.root, encoding="UTF-8", xml_declaration=True)

    def save(self, file_name: str = "bom.xml"):
        tree = ET.ElementTree(self.root)
        tree.write(file_name, encoding="UTF-8", xml_declaration=True)
