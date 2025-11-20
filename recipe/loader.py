import logging
from lxml import etree as ET
from pathlib import Path
import copy
import os
import uuid
import json
import html
from .registry import COMPONENTS

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

current_dir = os.path.dirname(os.path.abspath(__file__))
MAIN_TREE_PATH = os.path.join(current_dir, "../template/Bare.xml")
OUT_PATH = "assisted_recipe.xml"

# ---------------------------------------------------------
# Load main XML
# ---------------------------------------------------------
logger.debug("Loading main XML file: %s", MAIN_TREE_PATH)
main_tree = ET.parse(MAIN_TREE_PATH)
main_root = main_tree.getroot()

parent = main_root.find(".//eSpecXmlObjs/eProcObject[@objType='PM_OPERATION']")
if parent is None:
    raise RuntimeError("Target <eProcObject objType='PM_OPERATION'> not found")

logger.debug("Found PM_OPERATION node: %s", parent.tag)

# Load shared sequence template only once
sequence_path: Path = COMPONENTS["sequence"]["path"]
logger.debug("Loading sequence XML file: %s", sequence_path)
sequence_template = ET.parse(sequence_path).getroot()

# Create new GUID for PM_OPERATION
new_guid = str(uuid.uuid4())
parent.set("guid", new_guid)
logger.debug("Assigned new guid to PM_OPERATION: %s", new_guid)


X_POS = 300
Y_POS = 100
TOP   = 100
BREAK = 3 # Change Y_POS every BREAK number of phases


# ---------------------------------------------------------
# Helper: Load component element
# ---------------------------------------------------------
def update_object_config(elem):
    global X_POS, Y_POS, TOP

    logger.debug("Updating objectConfig for element id=%s", elem.get("instanceId"))

    # update coordinates
    logger.debug("Set xPos=%s yPos=%s", X_POS, Y_POS)
    elem.set("xPos", str(X_POS))
    elem.set("yPos", str(Y_POS))

    raw = elem.get("objectConfig")
    logger.debug("Raw objectConfig: %s", raw)

    if not raw:
        logger.debug("No objectConfig attribute found → skipping JSON update.")
        return elem

    try:
        json_str = html.unescape(raw)
        logger.debug("Unescaped JSON string: %s", json_str)

        config = json.loads(json_str)
        logger.debug("Parsed JSON successfully.")


        config["Label"]["left"] = X_POS - 18
        config["Label"]["top"] = TOP


        new_json = json.dumps(config, separators=(",", ":"))
        escaped = html.escape(new_json)

        elem.set("objectConfig", escaped)
        logger.debug("Updated objectConfig (escaped): %s", escaped)

    except Exception as e:
        logger.error("Failed to parse/update objectConfig: %s", e, exc_info=True)

    X_POS += 180
    TOP += 49

    logger.debug("Next X_POS=%s Y_POS=%s LEFT=%s TOP=%s", X_POS, Y_POS, X_POS - 12, TOP)

    return elem

def load_component_element(name: str) -> ET._Element:
    logger.debug("Loading component: %s", name)

    xml_path: Path = COMPONENTS[name]["path"]
    root = ET.parse(str(xml_path)).getroot()

    elem = root.find(".//eProcCompObject")
    if elem is None:
        logger.debug("Component file root is the object.")
        elem = root

    updated = update_object_config(elem)
    return updated



# ---------------------------------------------------------
# Insert components
# ---------------------------------------------------------
def insert_components_with_guid(component_names: list, out_path: str):
    global Y_POS, X_POS
    logger.debug("Starting component insertion...")

    insert_index = 0
    component_no = 2
    break_counter = 0

    seq_copy = copy.deepcopy(sequence_template)
    seq_copy.set("fromCompNo", "0")
    seq_copy.set("toCompNo", str(component_no))

    logger.debug("Inserting first sequence for CompNo: %s and InstanceId: %s", component_no, parent.get("instanceId"))
    parent.insert(insert_index, seq_copy)
    seq_copy.tail = "\t\t\t\n"

    for name in component_names:
        if break_counter % BREAK == 0:
            logger.debug("Breaking the transition line to a new line.")
            Y_POS += 120
            X_POS = 300
        logger.debug("Processing component: %s", name)

        component_guid = str(uuid.uuid4())
        comp_elem = load_component_element(name)

        # Work with a copy — do NOT modify original tree element
        comp_copy = copy.deepcopy(comp_elem)

        # Assign compNo
        if "compNo" in comp_copy.attrib:
            comp_copy.set("compNo", str(component_no))
            logger.debug("Set compNo=%s", component_no)

        if "instanceId" in comp_copy.attrib:
            id = str(name + "" + str(component_no))
            comp_copy.set("instanceId", id)
            logger.debug("Set instanceId=%s", id)

        # Assign component GUID
        if "guid" in comp_copy.attrib:
            comp_copy.set("guid", component_guid)
            logger.debug("Set component GUID=%s", component_guid)

        for data_line in comp_copy.findall(".//eProcCompDataLine"):
            if "guid" in data_line.attrib and "parent_guid" in data_line.attrib:
                data_line.set("parent_guid", new_guid)
                data_line.set("guid", component_guid)
                logger.debug("Updated data line: parent_guid=%s guid=%s", new_guid, component_guid)

        seq_copy = copy.deepcopy(sequence_template)
        seq_copy.set("fromCompNo", str(component_no - 1))
        seq_copy.set("toCompNo", str(component_no))

        logger.debug("Inserting sequence for CompNo: %s", component_no)
        parent.insert(insert_index, seq_copy)
        seq_copy.tail = "\t\t\t\n"
        insert_index += 1

        # Insert component
        logger.debug("Inserting component XML element...")
        parent.insert(insert_index, comp_copy)
        comp_copy.tail = "\t\t\t\n"

        insert_index += 1
        component_no += 1
        break_counter += 1

    # Final Transition Line
    seq_copy = copy.deepcopy(sequence_template)
    seq_copy.set("fromCompNo", str(component_no - 1))
    seq_copy.set("toCompNo", "-1")

    logger.debug("Inserting final sequence for CompNo: %s", component_no - 1)
    parent.insert(insert_index, seq_copy)
    seq_copy.tail = "\t\t\t\n"
    insert_index += 1

    logger.debug("Writing updated XML to: %s", out_path)
    main_tree.write(out_path, pretty_print=True, encoding="utf-8", xml_declaration=False)
    logger.info("XML updated successfully → %s", out_path)


# ---------------------------------------------------------
# Run Script
# ---------------------------------------------------------
if __name__ == "__main__":
    insert_components_with_guid(
        ["operator_instruction", "record_text", "operator_instruction", "operator_instruction", "record_text"],
        OUT_PATH
    )
    print("Wrote", OUT_PATH)
