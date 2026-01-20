import os
import re
import json
import requests

# --- Configuration ---
JSON_ROOT_DIR = r'C:\Users\khanrham\hamza\pomsicle\agentic\data\components'
API_URL = "https://c26bf85ed762.ngrok-free.app/ask"
SESSION_ID = "hk151817"

items = [
    "CheckInPallet", "AddPallet", "CheckOutEquipment", "OutputCount", 
    "ScanAndVerify", "CameraCapture", "RecordChecklist", "SendEmail", 
    "ViewReport", "AddDispenseKit", "AddExternalFile", "AddMaterial", 
    "AddUtility", "AdjustMaterialInventory", "AliquotSetup", 
    "AttachDocumentToLot", "AutoGlassLoad", "AutoGlassUnload", 
    "BufferFlush", "Calculation", "CallWebAPI", "CheckBOM", 
    "CheckCleaning", "CheckEquipmentState", "CheckInEquipment", 
    "CheckInMaterial", "ComplexSampleCollection", "ComplexSampleResult", 
    "Create Exception", "CultureData", "DisplayLotAttributes", 
    "EquipmentContents", "FlexibleAddMaterial", "FlexibleDataGrid", 
    "FlexibleRecordDevice", "GenerateXML", "GrossWeighDispense", 
    "InProcessTesting", "KeepTareDispense", "LaunchWorksheet", 
    "LineClearance", "ManageAssembly", "ManualDispense", 
    "MatrixMaterialAddition", "MiscBulkReceipt", "MiscDispenseSetup", 
    "MoveEquipment", "MoveMaterial", "OperatorInstruction", "Output", 
    "PCIEnhanced", "POBulkReceipt", "PrintInProcessLabel", 
    "PrintOutputLabel", "ProductWaste", "Quality", "RawMaterialSampling", 
    "Reconciliation", "Record Group Data", "RecordAnyEquipment", 
    "RecordContainerTare", "RecordDevice", "RecordIPT", 
    "RecordLotAttributes", "RecordProcessTime", "RecordQuantity", 
    "RecordRejectsAndSamples", "RecordRunID", "RecordText", 
    "RecordTime", "RecordValue", "ReportSDA", "SampleCollection", 
    "SampleResult", "SelectBatch", "SelectDispenseMethod", 
    "SelectMaterial", "SelectScale", "SetEquipmentState", "Spreadsheet", 
    "StandardDispense", "StandardizeScale", "TargetOnScaleDispense", 
    "TargetSeedDensity", "TransferMaterial", "TransferRemaining", 
    "TurboSelectDispense", "VerifyArea", "VerifyEquipmentAddPoint", 
    "VerifyMaterialInEquipment", "VerifyMaterialState", 
    "VerifyOPCParameters", "VerifyRawMaterial", "VerifyRoomCleaning", 
    "VerifySafety", "ViewDocument", "VolumeDispense", 
    "WarehouseDispense", "WriteOPCParameters", "Yield", "YieldWeigh", 
    "CheckInCarrier", "AddCarrier"
]

def to_snake_case(text):
    text = text.replace(" ", "")
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_existing_files(root_dir):
    existing = set()
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                existing.add(os.path.splitext(file)[0])
    return existing

def clean_json_string(raw_string):
    """Removes markdown code blocks and validates JSON."""
    # Remove ```json and ``` patterns
    cleaned = re.sub(r'```json\s*|\s*```', '', raw_string).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"Validation Error: {e}")
        return None

def process_items():
    existing_files = get_existing_files(JSON_ROOT_DIR)
    
    for item in items:
        file_name = to_snake_case(item)
        
        if file_name in existing_files:
            continue
        print(f"[!] {file_name}.json missing. Requesting data...")

        
        question_text = f"""What is the '{item}' phase and what does it do? 
Fill the information into the JSON structure provided below. 

Constraints:
1. Do not say "I don't know"; if information is missing, leave the field as "string", [], or {{}} as shown in the template.
2. Ensure the 'components' field within 'depends_on' includes specific phases if they are requirements.
3. Return ONLY the JSON object.

Template:
{{
  "id": "{item}",
  "category": "human | material | equipment | data | system | control | integration",
  "description": "string",
  "intent": "what this component is meant to accomplish",
  "inputs": {{}},
  "outputs": {{}},
  "depends_on": {{
    "components": [],
    "conditions": []
  }},
  "preconditions": [],
  "postconditions": [],
  "side_effects": [],
  "example_usage": "string"
}}"""

        payload = {"question": question_text, "top_k": 9, "session_id": SESSION_ID}

        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            full_response = response.json()
            
            # Extract the 'answer' field
            raw_answer = full_response.get("answer", "")
            
            # Validate and clean the nested JSON string
            valid_json_content = clean_json_string(raw_answer)
            
            if valid_json_content:
                save_path = os.path.join(JSON_ROOT_DIR, f"{file_name}.json")
                with open(save_path, 'w') as f:
                    json.dump(valid_json_content, f, indent=2)
                print(f"  [✓] Successfully saved.")
            else:
                print(f"  [X] Could not validate JSON from answer.")
                
        except Exception as e:
            print(f"  [X] Failed request for {item}: {e}")

if __name__ == "__main__":
    if not os.path.exists(JSON_ROOT_DIR):
        os.makedirs(JSON_ROOT_DIR)
    process_items()



