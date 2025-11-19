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