import os
import json
import shutil

def sort_components_by_category(root_path):
    categories = ["data", "equipment", "human", "material", "system", "control", "integration"]
    
    for cat in categories:
        cat_dir = os.path.join(root_path, cat)
        if not os.path.exists(cat_dir):
            os.makedirs(cat_dir)

    for root, dirs, files in os.walk(root_path):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    file_category = data.get("category", "").lower().strip()

                    if file_category in categories:
                        target_path = os.path.join(root_path, file_category, file_name)
                        
                        if os.path.abspath(file_path) != os.path.abspath(target_path):
                            shutil.move(file_path, target_path)
                            print(f"[✓] Moved: {file_name} -> /{file_category}/")
                    else:
                        print(f"[!] Unknown category '{file_category}' in {file_name}")

                except (json.JSONDecodeError, PermissionError) as e:
                    print(f"[X] Could not read {file_name}: {e}")

COMPONENTS_ROOT = r'C:\Users\khanrham\hamza\pomsicle\agentic\data\components'

if __name__ == "__main__":
    if os.path.exists(COMPONENTS_ROOT):
        sort_components_by_category(COMPONENTS_ROOT)
    else:
        print(f"Error: The folder '{COMPONENTS_ROOT}' was not found.")