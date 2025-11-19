import xml.etree.ElementTree as ET

main_tree = ET.parse("../template/Template.xml")
main_root = main_tree.getroot()
print("Main root is : ", main_root)
new_tree = ET.parse("../recipe/components/record_text.xml")
new_obj = new_tree.getroot()

target = main_root.find(".//eSpecXmlObjs/eProcObject[@objType='PM_OPERATION']/")
if target is None:
    raise ValueError("PM_OPERATION node not found")

target.append(new_obj)

main_tree.write("updated_main.xml", encoding="utf-8", xml_declaration=False)
