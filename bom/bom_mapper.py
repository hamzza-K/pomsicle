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
    TRANSACTION_ID = "BOM"
    SOURCE_SYSTEM = "Pomsicle"
    SOURCE_SITE_ID = "0001"
    TARGET_SYSTEM = "POMSnet"


# ========================= RECORD =======================
class Record:
    """Adds the records in the JSON or XML transaction payloads."""
    PLANT_ID = "Herndon"
    MATERIAL_ID = "100031"
    BOM_ID = ""
    BOP_ID = ""
    DESCRIPTION = ""
    EFFECTIVE_DATE = ""
    EXPIRATION_DATE = ""
    COMMENTS = ""
    BASE_QUANTITY = ""
    BASE_QUANTITY_UOM = ""

# ======================= LINE ITEM ======================
class LineItem:
    """Adds the line-item in the BOX object."""
    ITEM_REFERENCE_NO = "1"
    SUBSITUTION_NO = "1"
    ITEM_ID = "100013"
    ACTIVE_FLAG = "Yes"
    AGGREGATE_FLAG = "No"
    ADDITION_GROUP = ""
    ALLOW_BATCH_STAGING = ""
    ALLOW_WAREHOUSE_DISPENSE = ""
    CHECK_IN = "Yes"
    CHECK_WEIGH_RULE = ""
    CHECK_WEIGH_TOLERANCE = ""
    DISPENSE_COMMENT = "Test"
    DISPENSE_METHOD = ""
    DISPENSE_UOM = ""
    DISPENSE_AREA_TYPE = ""
    DISPENSE_AREA = ""
    DISPENSE_TOLERANCE_RULE = ""
    DISPENSE_TOLERANCE_LOWER = ""
    DISPENSE_TOLERANCE_UPPER = ""
    EQUIPMENT_CLASS = ""
    EXT_BOM_REF_NO = ""
    MATERIAL_QUANTITY = "10"
    MATERIAL_QUANTITY_UOM = "g"
    PERCENT_IN_YIELD = "100"
    OPTIMIZABLE = "Yes"
    SCALING_CLASS = "None"
    SCALING_RULE = "None"
    TRANSFER = "No"


def line_lookup(LineItem) -> dict:
    lineitem_look_up = {
        "ITEMREFERENCENUMBER": LineItem.ITEM_REFERENCE_NO,
        "SUBSTITUTIONNO": LineItem.SUBSITUTION_NO,
        "ITEMID": LineItem.ITEM_ID,
        "ACTIVEFLAG": LineItem.ACTIVE_FLAG,
        "AGGREGATEFLAG": LineItem.AGGREGATE_FLAG,
        "ADDITIONGROUP": LineItem.ADDITION_GROUP,
        "ALLOWBATCHSTAGING": LineItem.ALLOW_BATCH_STAGING,
        "ALLOWWAREHOUSEDISPENSE": LineItem.ALLOW_WAREHOUSE_DISPENSE,
        "CHECKIN": LineItem.CHECK_IN,
        "CHECKWEIGHRULE": LineItem.CHECK_WEIGH_RULE,
        "CHECKWEIGHTOLERANCE": LineItem.CHECK_WEIGH_TOLERANCE,
        "DISPENSECOMMENT": LineItem.DISPENSE_COMMENT,
        "DISPENSEMETHOD": LineItem.DISPENSE_METHOD,
        "DISPENSEUOM": LineItem.DISPENSE_UOM,
        "DISPENSEAREATYPE": LineItem.DISPENSE_AREA_TYPE,
        "DISPENSEAREA": LineItem.DISPENSE_AREA,
        "DISPENSETOLERANCERULE": LineItem.DISPENSE_TOLERANCE_RULE,
        "DISPENSETOLERANCELOWER": LineItem.DISPENSE_TOLERANCE_LOWER,
        "DISPENSETOLERANCEUPPER": LineItem.DISPENSE_TOLERANCE_UPPER,
        "EQUIPMENTCLASS": LineItem.EQUIPMENT_CLASS,
        "EXT_BOM_REF_NO": LineItem.EXT_BOM_REF_NO,
        "MATERIALQUANTITY": LineItem.MATERIAL_QUANTITY,
        "MATERIALQUANTITYUOM": LineItem.MATERIAL_QUANTITY_UOM,
        "OPTIMIZABLE": LineItem.OPTIMIZABLE,
        "SCALECLASS": LineItem.SCALING_CLASS,
        "SCALINGRULE": LineItem.SCALING_RULE,
        "PERCENTINYIELD": LineItem.SCALING_RULE,
        "TRANSFER": LineItem.TRANSFER
    }


    return lineitem_look_up

def header_lookup(Header) -> dict:
    header_look_up = {
        "TransactionID": Header.TRANSACTION_ID,
        "TransactionTimeStamp": Header.TIMESTAMP,
        "TransactionRefID": Header.TRANSACTION_REF_ID,
        "SourceSystem": Header.SOURCE_SYSTEM,
        "SourceSiteID": Header.SOURCE_SITE_ID,
        "TargetSystem": Header.TARGET_SYSTEM
    }

    return header_look_up


def record_lookup(Record) -> dict:
    record_look_up = {
        "PLANTID": Record.PLANT_ID,
        "MATERIALID": Record.MATERIAL_ID,
        "BOMID": Record.BOM_ID,
        "BOPID": Record.BOP_ID,
        "DESCRIPTION": Record.DESCRIPTION,
        "EFFECTIVITYDATE": Record.EFFECTIVE_DATE,
        "EXPIRATIONDATE": Record.EXPIRATION_DATE,
        "COMMENTS": Record.COMMENTS,
        "BASEQUANTITY": Record.BASE_QUANTITY,
        "BASEQUANTITYUOM": Record.BASE_QUANTITY_UOM
    }

    return record_look_up
