import logging
from lxml import etree as ET
from pathlib import Path
import copy
import os
import uuid
import json
import html
from .registry import COMPONENTS

logger = logging.getLogger(__name__)


class RecipeBuilder:
    """
    Handles creation of recipes by inserting XML components
    into a base template with proper GUIDs and layout positions.
    """

    def __init__(self, main_template: str = "../template/Bare.xml"):
        # Paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.main_template_path = os.path.join(self.current_dir, main_template)
        self.main_tree = ET.parse(self.main_template_path)
        self.main_root = self.main_tree.getroot()

        self.parent = self.main_root.find(".//eSpecXmlObjs/eProcObject[@objType='PM_OPERATION']")
        if self.parent is None:
            raise RuntimeError("Target <eProcObject objType='PM_OPERATION'> not found")

        # Assign new GUID for PM_OPERATION
        self.new_guid = str(uuid.uuid4())
        self.parent.set("guid", self.new_guid)
        logger.debug("Assigned new guid to PM_OPERATION: %s", self.new_guid)

        # Load sequence template once
        sequence_path = COMPONENTS["sequence"]["path"]
        self.sequence_template = ET.parse(sequence_path).getroot()

        # Layout positions
        self.X_POS = 300
        self.Y_POS = 100
        self.TOP = 100
        self.BREAK = 3

    def attach_bill(self, bom_path: str, output_path: str = "Assisted.xml"):
        """
        Insert a Bill of Materials component into the recipe.
        The BOM (<eBoxObject>) is inserted right after the <eProcObject objType="PM_SUP"> element closes.
        
        Args:
            bom_path: Path to the BOM XML file to attach.
            output_path: Optional path to write the updated XML. If None, doesn't write.
        """
        recipe_path = os.path.join(self.current_dir, output_path)
        e_spec_xml_objs = ET.parse(recipe_path).getroot().find(".//eSpecXmlObjs")
        if e_spec_xml_objs is None:
            raise RuntimeError("Target <eSpecXmlObjs> not found for attaching BOM")
        
        # Find the PM_SUP (Unit Procedure) element
        pm_sup = e_spec_xml_objs.find(".//eProcObject[@objType='PM_SUP']")
        if pm_sup is None:
            logger.warning("PM_SUP element not found, appending BOM to end of eSpecXmlObjs")
            parent = e_spec_xml_objs
            insert_index = len(list(parent))
        else:
            parent = pm_sup.getparent()
            if parent is None:
                parent = e_spec_xml_objs
            
            parent_children = list(parent)
            try:
                insert_index = parent_children.index(pm_sup) + 1
            except ValueError:
                insert_index = len(parent_children)
        
        bom_tree = ET.parse(bom_path)
        bom_root = bom_tree.getroot()
        bom_spec_objs = bom_root.find(".//eSpecXmlObjs")
        
        if bom_spec_objs is None:
            raise RuntimeError(f"BOM file '{bom_path}' does not contain <eSpecXmlObjs> element")
        
        bom_box_object = bom_spec_objs.find(".//eBoxObject[@objType='MM_BOM']")
        if bom_box_object is None:
            raise RuntimeError(f"BOM file '{bom_path}' does not contain <eBoxObject objType='MM_BOM'> element")
        
        bom_copy = copy.deepcopy(bom_box_object)
        
        parent.insert(insert_index, bom_copy)

        logger.info("Attached BOM to recipe: %s", recipe_path)
        
        if output_path:
            self.main_tree.write(recipe_path, pretty_print=True, encoding="utf-8", xml_declaration=False)
            logger.info("Updated BOM XML written to: %s", recipe_path)

    def _update_object_config(self, elem: ET._Element) -> ET._Element:
        """Update objectConfig JSON and coordinates for a component."""
        logger.info("Updating objectConfig for element id=%s", elem.get("instanceId"))

        # Set coordinates
        elem.set("xPos", str(self.X_POS))
        elem.set("yPos", str(self.Y_POS))

        raw = elem.get("objectConfig")
        if raw:
            try:
                config = json.loads(html.unescape(raw))
                config["Label"]["left"] = self.X_POS - 18
                config["Label"]["top"] = self.TOP
                escaped = html.escape(json.dumps(config, separators=(",", ":")))
                elem.set("objectConfig", escaped)
            except Exception as e:
                logger.error("Failed to update objectConfig: %s", e, exc_info=True)

        self.X_POS += 180
        self.TOP += 49
        return elem

    def _load_component_element(self, name: str) -> ET._Element:
        """Load a component XML element and update objectConfig."""
        xml_path = COMPONENTS[name]["path"]
        root = ET.parse(str(xml_path)).getroot()
        elem = root.find(".//eProcCompObject") or root
        return self._update_object_config(elem)

    def insert_components(self, component_names: list[str], out_path: str):
        """Insert a list of components into the main recipe template."""
        insert_index = 0
        component_no = 2
        break_counter = 0

        # Insert first sequence
        seq_copy = copy.deepcopy(self.sequence_template)
        seq_copy.set("fromCompNo", "0")
        seq_copy.set("toCompNo", str(component_no))
        self.parent.insert(insert_index, seq_copy)
        seq_copy.tail = "\t\t\t\n"

        for name in component_names:
            if break_counter % self.BREAK == 0:
                self.Y_POS += 120
                self.X_POS = 300

            component_guid = str(uuid.uuid4())
            comp_elem = copy.deepcopy(self._load_component_element(name))

            # Set compNo, instanceId, and GUID
            if "compNo" in comp_elem.attrib:
                comp_elem.set("compNo", str(component_no))
            if "instanceId" in comp_elem.attrib:
                comp_elem.set("instanceId", f"{name}{component_no}")
                logger.info(f"Changed instanceId to {comp_elem.get('instanceId')}")
            if "guid" in comp_elem.attrib:
                comp_elem.set("guid", component_guid)

            for data_line in comp_elem.findall(".//eProcCompDataLine"):
                if "guid" in data_line.attrib and "parent_guid" in data_line.attrib:
                    data_line.set("parent_guid", self.new_guid)
                    data_line.set("guid", component_guid)

            # Insert transition sequence before the component
            seq_copy = copy.deepcopy(self.sequence_template)
            seq_copy.set("fromCompNo", str(component_no - 1))
            seq_copy.set("toCompNo", str(component_no))
            self.parent.insert(insert_index, seq_copy)
            seq_copy.tail = "\t\t\t\n"
            insert_index += 1

            # Insert component
            self.parent.insert(insert_index, comp_elem)
            comp_elem.tail = "\t\t\t\n"
            insert_index += 1
            component_no += 1
            break_counter += 1

        # Insert final transition sequence
        seq_copy = copy.deepcopy(self.sequence_template)
        seq_copy.set("fromCompNo", str(component_no - 1))
        seq_copy.set("toCompNo", "-1")
        self.parent.insert(insert_index, seq_copy)
        seq_copy.tail = "\t\t\t\n"

        # Write output
        self.main_tree.write(out_path, pretty_print=True, encoding="utf-8", xml_declaration=False)
        logger.info("XML updated successfully → %s", out_path)
        return out_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    builder = RecipeBuilder()
    builder.insert_components(
        ["operator_instruction", "record_text", "operator_instruction"],
        "assisted_recipe.xml"
    )
    print("Wrote assisted_recipe.xml")