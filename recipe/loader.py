import logging
from lxml import etree as ET
from pathlib import Path
import copy
import uuid
from registry import COMPONENTS

# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------
MAIN_TREE_PATH = "../template/Template.xml"
OUT_PATH = "updated.xml"

# ---------------------------------------------------------
# Load main XML
# ---------------------------------------------------------
logging.debug("Loading main XML file: %s", MAIN_TREE_PATH)
main_tree = ET.parse(MAIN_TREE_PATH)
main_root = main_tree.getroot()

parent = main_root.find(".//eSpecXmlObjs/eProcObject[@objType='PM_OPERATION']")
if parent is None:
    raise RuntimeError("Target <eProcObject objType='PM_OPERATION'> not found")

logging.debug("Found PM_OPERATION node: %s", parent.tag)

# Load shared sequence template only once
sequence_path: Path = COMPONENTS["sequence"]["path"]
logging.debug("Loading sequence XML file: %s", sequence_path)
sequence_template = ET.parse(sequence_path).getroot()

# Create new GUID for PM_OPERATION
new_guid = str(uuid.uuid4())
parent.set("guid", new_guid)
logging.debug("Assigned new guid to PM_OPERATION: %s", new_guid)


# ---------------------------------------------------------
# Helper: Load component element
# ---------------------------------------------------------
def load_component_element(name: str) -> ET._Element:
    logging.debug("Loading component: %s", name)

    if name not in COMPONENTS:
        raise ValueError(f"Component '{name}' not found in registry")

    xml_path: Path = COMPONENTS[name]["path"]
    if not xml_path.exists():
        raise FileNotFoundError(f"Component file not found: {xml_path}")

    logging.debug("Parsing component XML from: %s", xml_path)
    root = ET.parse(str(xml_path)).getroot()

    comp_elem = root.find(".//eProcCompObject")
    if comp_elem is None:
        logging.debug("Component root used directly (no eProcCompObject found).")
        comp_elem = root

    return comp_elem


# ---------------------------------------------------------
# Insert components
# ---------------------------------------------------------
def insert_components_with_guid(component_names: list, out_path: str):
    logging.debug("Starting component insertion...")

    insert_index = 0
    component_no = 2  # PM_PHASE starts at 1, components next

    for name in component_names:
        logging.debug("Processing component: %s", name)

        component_guid = str(uuid.uuid4())
        comp_elem = load_component_element(name)

        # Work with a copy — do NOT modify original tree element
        comp_copy = copy.deepcopy(comp_elem)

        # Assign compNo
        if "compNo" in comp_copy.attrib:
            comp_copy.set("compNo", str(component_no))
            logging.debug("Set compNo=%s", component_no)

        if "instanceId" in comp_copy.attrib:
            id = str(name + "" + str(component_no))
            comp_copy.set("instanceId", id)
            logging.debug("Set instanceId=%s", id)

        # Assign component GUID
        if "guid" in comp_copy.attrib:
            comp_copy.set("guid", component_guid)
            logging.debug("Set component GUID=%s", component_guid)

        # Fix eProcCompDataLine attributes
        for data_line in comp_copy.findall(".//eProcCompDataLine"):
            if "guid" in data_line.attrib and "parent_guid" in data_line.attrib:
                data_line.set("parent_guid", new_guid)
                data_line.set("guid", component_guid)
                logging.debug("Updated data line: parent_guid=%s guid=%s", new_guid, component_guid)

        # Insert sequence BEFORE component
        seq_copy = copy.deepcopy(sequence_template)
        seq_copy.set("fromCompNo", str(component_no - 1))
        seq_copy.set("toCompNo", str(component_no - 1))

        logging.debug("Inserting sequence for CompNo: %s", component_no)
        parent.insert(insert_index, seq_copy)
        insert_index += 1

        # Insert component
        logging.debug("Inserting component XML element...")
        parent.insert(insert_index, comp_copy)
        insert_index += 1

        component_no += 1

    logging.debug("Writing updated XML to: %s", out_path)
    main_tree.write(out_path, pretty_print=True, encoding="utf-8", xml_declaration=False)
    logging.info("XML updated successfully → %s", out_path)


# ---------------------------------------------------------
# Run Script
# ---------------------------------------------------------
if __name__ == "__main__":
    insert_components_with_guid(
        ["operator_instruction", "record_text", "operator_instruction"],
        OUT_PATH
    )
    print("Wrote", OUT_PATH)
