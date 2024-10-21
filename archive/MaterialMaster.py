import secrets
from datetime import datetime


# ========================== HEADER =======================
class Header:
    """Adds the header in the JSON or XML payloads. This is Optional."""

    def __init__(self):
        self._timestamp = None
        self._transaction_ref_id = None

    @property
    def TIMESTAMP(self):
        if self._timestamp is None:
            self._timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
           
        return self._timestamp

    @property
    def TRANSACTION_REF_ID(self):
        if self._transaction_ref_id is None:
            self.transaction_ref_id = secrets.token_hex(16)
        return self.transaction_ref_id
    
    #TIMESTAMP = datetime.now().isoformat()
    #TRANSACTION_REF_ID = secrets.token_hex(16)
    TRANSACTION_ID = "MATERIAL_MASTER"
    SOURCE_SYSTEM = "Demo"
    SOURCE_SITE_ID = "1111"
    TARGET_SYSTEM = "POMSnet"


# ========================= RECORD =======================
class Record:
    """Adds the records in the JSON or XML transaction payloads."""
    PLANT_ID = "Herndon"
    DEFAULT_QUALITY = "Released"
    INVENTORY_TRACKING = "Container"
    INVENTORY_UOM = "kg"
    MATERIAL_TYPE = "Raw Material"
    STORAGE_CONDITION = "AMBIENT"
    MATERIAL_STATE = "0"

def header_lookup(Header) -> dict:
    header_look_up = {
        Header.TRANSACTION_ID: "TransactionID",
        Header.TIMESTAMP: "TransactionTimeStamp",
        Header.TRANSACTION_REF_ID: "TransactionRefID",
        Header.SOURCE_SYSTEM: "SourceSystem",
        Header.SOURCE_SITE_ID: "SourceSiteID",
        Header.TARGET_SYSTEM: "TargetSystem",
    }

    return header_look_up

    #Defines the Record Attribute in Payload. For example:
    # PlantID would be the key and the value would be its corresponding value defined above. 
def record_lookup(Record) -> dict:
    record_look_up = {
        Record.PLANT_ID: "PlantID",
        Record.DEFAULT_QUALITY: "DefaultQuality",
        Record.INVENTORY_TRACKING: "InventoryTracking",
        Record.INVENTORY_UOM: "InventoryUOM",
        Record.MATERIAL_TYPE: "MaterialType",
        Record.STORAGE_CONDITION: "StorageCondition",
        Record.MATERIAL_STATE: "MaterialState",
        # Record.SHELF_LIFE: "ShelfLife",
        # Record.SHELF_LIFE_UOM: "ShelfLifeUOM",
    }

    return record_look_up
