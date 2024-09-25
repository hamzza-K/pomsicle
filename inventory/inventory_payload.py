from typing import Iterator, Optional
from inventory.inventory_structure import record_lookup, header_lookup, Record, Header, Inventory

class Payload:
    """Returns the string representation of the BOM"""
    def __init__(self, type: str = "xml") -> None:
        self.trans = Inventory()
    
    def fetch(self, records: Iterator = None, save: bool = Optional[False]) -> str:
        """record is a singular row of the excel sheet"""
        # Create instances of Header, Record, and LineItem
        header = Header()
        record_instance = Record()
        
        # Fill in Header information
        for header_attr, xml_element in header_lookup(header).items():
            self.trans.add_header(header_attr, xml_element)
            # self.trans.add_header(getattr(header, header_attr), xml_element)
        
        # Fill in Record information
        for record_attr, xml_element in record_lookup(record_instance).items():
            self.trans.add_record(record_attr, xml_element)
            

        if save:
            return self.trans.save("inventory.xml")
        return self.trans.to_string()
