import os

def get_xml_names(directory):
    """Get names of .xml files in the top-level directory."""
    return {os.path.splitext(f)[0] for f in os.listdir(directory) if f.endswith('.xml')}

def get_json_names_recursive(directory):
    """Search through all subdirectories for .json files."""
    json_names = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_names.add(os.path.splitext(file)[0])
    return json_names

def compare_directories(xml_dir, json_root):
    xml_files = get_xml_names(xml_dir)
    json_files = get_json_names_recursive(json_root)

    all_names = sorted(xml_files.union(json_files))

    # Table Header
    print("-" * 75)
    print(f"{'XML File Name':<30} | {'JSON File Name':<30} | {'Match'}")
    print("-" * 75)

    for name in all_names:
        xml_exists = name if name in xml_files else "---"
        json_exists = name if name in json_files else "---"
        
        status = "✓" if (name in xml_files and name in json_files) else "✗"
        
        print(f"{xml_exists:<30} | {json_exists:<30} | {status}")



XML_FOLDER_PATH = r'C:\Users\khanrham\hamza\pomsicle\recipe\components'
JSON_FOLDER_PATH = r'C:\Users\khanrham\hamza\pomsicle\agentic\data\components'

if __name__ == "__main__":
    if os.path.exists(XML_FOLDER_PATH) and os.path.exists(JSON_FOLDER_PATH):
        compare_directories(XML_FOLDER_PATH, JSON_FOLDER_PATH)
    else:
        print("Error: Check your directory paths.")

