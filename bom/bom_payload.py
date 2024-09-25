from typing import Iterator
from datetime import datetime
import polars as pl
from bom_structure import BOM_XML
from bom_mapper import record_lookup, header_lookup, line_lookup, Record, Header, LineItem

class Payload:
    """Returns the string representation of the BOM"""
    def __init__(self, type: str = "xml") -> None:
        self.trans = BOM_XML()
    
    def fetch(self, records: Iterator = None) -> str:
        """record is a singular row of the excel sheet"""
        # Create instances of Header, Record, and LineItem
        header = Header()
        record_instance = Record()
        line_item_instance = LineItem()
        
        # Fill in Header information
        for header_attr, xml_element in header_lookup(header).items():
            self.trans.add_header(header_attr, xml_element)
        
        # Fill in Record information
        for record_attr, xml_element in record_lookup(record_instance).items():
            self.trans.add_record(record_attr, xml_element)
        
        # Add line items
        for record in records.iter_rows():
            line_item_instance.ITEM_REFERENCE_NO = record[0]
            line_item_instance.SUBSITUTION_NO = record[11]
            line_item_instance.ITEM_ID = str(record[1])
            line_item_instance.ACTIVE_FLAG = record[12]
            line_item_instance.AGGREGATE_FLAG = record[10]
            line_item_instance.ADDITION_GROUP = record[13]
            line_item_instance.ALLOW_BATCH_STAGING = record[14]
            line_item_instance.ALLOW_WAREHOUSE_DISPENSE = record[15]
            line_item_instance.CHECK_IN = record[16]
            line_item_instance.CHECK_WEIGH_RULE = record[17]
            line_item_instance.CHECK_WEIGH_TOLERANCE = record[18]
            line_item_instance.DISPENSE_COMMENT = record[2]
            line_item_instance.DISPENSE_METHOD = record[19]
            line_item_instance.DISPENSE_UOM = record[6]
            line_item_instance.DISPENSE_AREA_TYPE = record[3]
            line_item_instance.DISPENSE_AREA = record[4]
            line_item_instance.DISPENSE_TOLERANCE_RULE = record[20]
            line_item_instance.DISPENSE_TOLERANCE_LOWER = record[21]
            line_item_instance.DISPENSE_TOLERANCE_UPPER = record[22]
            line_item_instance.EQUIPMENT_CLASS = record[23]
            line_item_instance.EXT_BOM_REF_NO = record[24]
            line_item_instance.MATERIAL_QUANTITY = record[5]
            line_item_instance.MATERIAL_QUANTITY_UOM = record[6]
            line_item_instance.PERCENT_IN_YIELD = record[25] # Change the location of this in sheet
            line_item_instance.OPTIMIZABLE = record[9]
            line_item_instance.SCALING_CLASS = record[0]
            line_item_instance.SCALING_RULE = record[7]
            line_item_instance.TRANSFER = record[8]
            for line_item_attr, xml_element in line_lookup(line_item_instance).items():
                self.trans.add_line_item(line_item_attr, xml_element)
            self.trans.line = None # This will add <LineItem> tag after the end of one BOM item.

            
        return self.trans.save("bom.xml")

if __name__ == '__main__':
    Payload().fetch()
