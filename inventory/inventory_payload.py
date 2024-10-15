from typing import Iterator, Optional
from inventory.inventory_structure import record_lookup, header_lookup, Record, Header, InventoryJSON

class Payload:
    """Returns the string representation of the Inventory"""
    
    def fetch(self, record: Iterator = None, save: bool = False) -> str:
        """record is a singular row of the excel sheet"""
        self.trans = InventoryJSON()

        header = Header()
        record_instance = Record()

        record_instance.MATERIAL_ID = record[0]
        record_instance.PLANT_ID = record[2]
        record_instance.MATERIAL_QTY = f"{record[6]:.2f}"
        record_instance.LOCATION_ID = record[5]
        record_instance.UOM = record[7]
        record_instance.MATERIAL_TYPE = record[8]
        record_instance.CONTAINER_ID = record[9]
        record_instance.LOT_ID = record[1]
        record_instance.LOT_STATUS = record[3]
        record_instance.AREA_ID = record[5]


        # Fill in Header information
        for header_attr, xml_element in header_lookup(header).items():
            self.trans.add_header(header_attr, xml_element)
            # self.trans.add_header(getattr(header, header_attr), xml_element)
        
        # Fill in Record information
        for record_attr, xml_element in record_lookup(record_instance).items():
            self.trans.add_record(record_attr, xml_element)
            

        if save:
            return self.trans.save("inventory.json")
        return self.trans.to_string()
