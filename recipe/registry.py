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
        "description": "Record time component for capturing operator inputs.",
        "category": "root",
    },
    "add_external_file": {
        "path": BASE_DIR / "components" / "add_external_file.xml",
        "description": "Add external file component.",
        "category": "root",
    },
    "add_material": {
        "path": BASE_DIR / "components" / "add_material.xml",
        "description": "Add material to the recipe.",
        "category": "root",
    },
    "adjust_material_inventory": {
        "path": BASE_DIR / "components" / "adjust_material_inventory.xml",
        "description": "Adjust material inventory.",
        "category": "root",
    },
    "aliquot": {
        "path": BASE_DIR / "components" / "aliquot.xml",
        "description": "Aliquot material component.",
        "category": "root",
    },
    "buffer_flush": {
        "path": BASE_DIR / "components" / "buffer_flush.xml",
        "description": "Buffer flush operation.",
        "category": "root",
    },
    "calculation": {
        "path": BASE_DIR / "components" / "calculation.xml",
        "description": "Calculation phase component.",
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
    "check_in_material": {
        "path": BASE_DIR / "components" / "check_in_material.xml",
        "description": "Check in material.",
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
    "record_text": {
        "path": BASE_DIR / "components" / "record_text.xml",
        "description": "Record text component for capturing operator inputs.",
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