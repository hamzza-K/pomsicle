from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

COMPONENTS = {
    "operator_instruction": {
        "path": BASE_DIR / "components" / "operator_instruction.xml",
        "description": "Gives choices and instructions to operators.",
        "category": "root",
    },
    "record_text": {
        "path": BASE_DIR / "components" / "record_text.xml",
        "description": "Record text component for capturing operator inputs.",
        "category": "root",
    },
    "record_time": {
        "path": BASE_DIR / "components" / "record_time.xml",
        "description": "Captures and records time set by operators.",
        "category": "root",
    },
    "record_process_time": {
        "path": BASE_DIR / "components" / "record_process_time.xml",
    },
    "add_external_file": {
        "path": BASE_DIR / "components" / "add_external_file.xml",
        "description": "Phase that allows attaching an external file to the batch by specifying a link.",
        "category": "root",
    },
    "add_material": {
        "path": BASE_DIR / "components" / "add_material.xml",
        "description": "Add material to the recipe.",
        "category": "root",
    },
    # --- Matched agentic/recipe components ---
    "calculation": {
        "path": BASE_DIR / "components" / "calculation.xml",
        "description": "Phase that defines calculation variables whose values can be used to pre-populate fields in other phases.",
        "category": "root",
    },
    "spread_sheet": {
        "path": BASE_DIR / "components" / "spread_sheet.xml",
        "description": "Performs spreadsheet-based calculations using recipe variables and operator inputs, displays input and output sheets, and records results.",
        "category": "root",
    },
    "verify_equipment_add_point": {
        "path": BASE_DIR / "components" / "verify_equipment_add_point.xml",
        "description": "Verified add point assignments for equipment, with QC pass/fail results.",
        "category": "root",
    },
    "verify_material_in_equipment": {
        "path": BASE_DIR / "components" / "verify_material_in_equipment.xml",
        "description": "Verifies that the specified material is present in each equipment of a defined class and validates each material's quantity, expiry date, and reset date.",
        "category": "root",
    },
    "check_in_material": {
        "path": BASE_DIR / "components" / "check_in_material.xml",
        "description": "Checks in material lots and records exceptions if needed.",
        "category": "root",
    },
    "adjust_material_inventory": {
        "path": BASE_DIR / "components" / "adjust_material_inventory.xml",
        "description": "Allows operators to adjust material inventory quantities and record reasons.",
        "category": "root",
    },
    "aliquot": {
        "path": BASE_DIR / "components" / "aliquot.xml",
        "description": "Splits material into aliquots and records relevant data.",
        "category": "root",
    },
    "add_utility": {
        "path": BASE_DIR / "components" / "add_utility.xml",
        "description": "Adds utility material to equipment and records exceptions if needed.",
        "category": "root",
    },
    "add_dispense_kit": {
        "path": BASE_DIR / "components" / "add_dispense_kit.xml",
        "description": "Allows containers that are kitted together to be automatically consumed when their kit ID is scanned.",
        "category": "root",
    },
    "scan_and_verify": {
        "path": BASE_DIR / "components" / "scan_and_verify.xml",
        "description": "Enables the operator to scan or manually enter a set of values and verify them against a configured list of expected values.",
        "category": "root",
    },
    "record_text": {
        "path": BASE_DIR / "components" / "record_text.xml",
        "description": "Records multi-line text, date/time, or entries from the operator.",
        "category": "root",
    },
    "call_web_api": {
        "path": BASE_DIR / "components" / "call_web_api.xml",
        "description": "Call web API component.",
        "category": "root",
    },
    "check_equipment_state": {
        "path": BASE_DIR / "components" / "check_equipment_state.xml",
        "description": "Check equipment state.",
        "category": "root",
    },
    "check_in_equipment": {
        "path": BASE_DIR / "components" / "check_in_equipment.xml",
        "description": "Check in equipment.",
        "category": "root",
    },
    "check_out_equipment": {
        "path": BASE_DIR / "components" / "check_out_equipment.xml",
        "description": "Check out equipment.",
        "category": "root",
    },
    "create_exception": {
        "path": BASE_DIR / "components" / "create_exception.xml",
        "description": "Create exception during recipe execution.",
        "category": "root",
    },
    "culture_data": {
        "path": BASE_DIR / "components" / "culture_data.xml",
        "description": "Culture data phase.",
        "category": "root",
    },
    "equipment_contents": {
        "path": BASE_DIR / "components" / "equipment_contents.xml",
        "description": "Equipment contents check-in phase.",
        "category": "root",
    },
    "flexible_add_material": {
        "path": BASE_DIR / "components" / "flexible_add_material.xml",
        "description": "Add materials to a production split.",
        "category": "root",
    },
    "generate_xml": {
        "path": BASE_DIR / "components" / "generate_xml.xml",
        "description": "Generate XML file phase.",
        "category": "root",
    },
    "manual_finish": {
        "path": BASE_DIR / "components" / "manual_finish.xml",
        "description": "Manual finish workflow component.",
        "category": "root",
    },
    "matrix_material_addition": {
        "path": BASE_DIR / "components" / "matrix_material_addition.xml",
        "description": "Matrix material addition phase.",
        "category": "root",
    },
    "move_material": {
        "path": BASE_DIR / "components" / "move_material.xml",
        "description": "Move material phase.",
        "category": "root",
    },
    "operator_instruction": {
        "path": BASE_DIR / "components" / "operator_instruction.xml",
        "description": "Gives choices and instructions to operators.",
        "category": "root",
    },
    "output": {
        "path": BASE_DIR / "components" / "output.xml",
        "description": "Output phase component.",
        "category": "root",
    },
    "record_container_tare": {
        "path": BASE_DIR / "components" / "record_container_tare.xml",
        "description": "Record container tare phase.",
        "category": "root",
    },
    "scan_and_verify": {
        "path": BASE_DIR / "components" / "scan_and_verify.xml",
        "description": "Scan and verify material phase.",
        "category": "root",
    },
    "spread_sheet": {
        "path": BASE_DIR / "components" / "spread_sheet.xml",
        "description": "Spreadsheet phase component.",
        "category": "root",
    },
    "verify_equipment_add_point": {
        "path": BASE_DIR / "components" / "verify_equipment_add_point.xml",
        "description": "Verify equipment add point phase.",
        "category": "root",
    },
    "verify_opc": {
        "path": BASE_DIR / "components" / "verify_opc.xml",
        "description": "Verify OPC phase.",
        "category": "root",
    },
    "write_opc": {
        "path": BASE_DIR / "components" / "write_opc.xml",
        "description": "Write OPC phase.",
        "category": "root",
    },
    "verify_material_in_equipment": {
        "path": BASE_DIR / "components" / "verify_material_in_equipment.xml",
        "description": "Verify material in equipment phase.",
        "category": "root",
    },
    "yield": {
        "path": BASE_DIR / "components" / "yield.xml",
        "description": "Yield phase component.",
        "category": "root",
    },
    "send_email": {
        "path": BASE_DIR / "components" / "send_email.xml",
        "description": "Send email phase component.",
        "category": "root",
    },

    "manual_finish": {
        "path": BASE_DIR / "components" / "manual_finish.xml",
        "description": "Manual finish workflow component.",
        "category": "root",
    },
    # Base components
    "base_operator_instruction": {
        "path": BASE_DIR / "components" / "base_components" / "operator_instruction.xml",
        "description": "Base operator instruction template.",
        "category": "base",
    },
    "base_record_text": {
        "path": BASE_DIR / "components" / "base_components" / "record_text.xml",
        "description": "Base record text template.",
        "category": "base",
    },
    # Sequence
    "sequence": {
        "path": BASE_DIR / "components" / "sequence.xml",
        "description": "Transition lines connecting the phases.",
        "category": "base",
    }
}