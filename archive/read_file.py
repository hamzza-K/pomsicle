from typing import Iterator
from MaterialMaster import record_lookup, header_lookup, Record, Header
from pomstransaction import POMSTransactionXML, POMSTransactionJSON

Header = Header()
Record = Record()


class Payload:
    """Returns the string representation of the Material"""
    def __init__(self, type: str = "json") -> None:
        self.trans = POMSTransactionXML() if type == "xml" else POMSTransactionJSON()
    
    def fetch(self, record: Iterator) -> str:
        """record is a singular row of the excel sheet"""
        Record.PLANT_ID = record[2]
        Record.DEFAULT_QUALITY = record[3]
        Record.INVENTORY_TRACKING = record[4]
        Record.INVENTORY_UOM = record[5]
        Record.MATERIAL_TYPE = record[6] 
        Record.STORAGE_CONDITION = record[8]
        Record.MATERIAL_STATE = record[7]


        record_look_up = record_lookup(Record)
        header_look_up = header_lookup(Header)

        for k, v in header_look_up.items():
            self.trans.add_header(v, k)

        for k, v in record_look_up.items():
            self.trans.add_record(v, k)

        self.trans.add_record("MaterialID", str(record[0]))
        self.trans.add_record("MaterialDescription", str(record[1]))

        return self.trans.to_string()

