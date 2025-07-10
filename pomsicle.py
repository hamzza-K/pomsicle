import os
import sys
import argparse
import logging
from banners import Banner
from inventory.read_inventory import read_file as read_inventory
from credentials import login
from config import config
from receive.receiving import ReceiveManager
from template.recipe_template import PomsicleTemplateManager

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_script_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

script_directory = get_script_dir()
config_folder_name = 'config'
config_file_name = 'config.cfg'

# --- Global Configuration ---
try:
    settings = config(translator='pomsicle')
    receive_settings = config(translator='pomsicle:receive')
except (FileNotFoundError, ValueError) as e:
    logger.critical(f"Configuration error: {e}. Exiting.")
    exit(1)

USERNAME = settings.get('USERNAME')
PASSWORD = settings.get('PASSWORD')

# --- Banner Display ---
ban = Banner()
print(r"""
 ________    ________      _____ ______       ________       ___      ________      ___           _______      
|\   __  \  |\   __  \    |\   _ \  _   \    |\   ____\     |\  \    |\   ____\    |\  \         |\  ___ \     
\ \  \|\  \ \ \  \|\  \   \ \  \\\__\ \  \   \ \  \___|_    \ \  \   \ \  \___|    \ \  \        \ \   __/|    
 \ \   ____\ \ \  \\\  \   \ \  \\|__| \  \   \ \_____  \    \ \  \   \ \  \        \ \  \        \ \  \_|/__  
  \ \  \___|  \ \  \\\  \   \ \  \    \ \  \   \|____|\  \    \ \  \   \ \  \____    \ \  \____    \ \  \_|\ \ 
   \ \__\      \ \_______\   \ \__\    \ \__\    ____\_\  \    \ \__\   \ \_______\   \ \_______\   \ \_______\
    \|__|       \|_______|    \|__|     \|__|   |\_________\    \|__|    \|_______|    \|_______|    \|_______|
                                                \|_________|                                                   
                                                          
""")

# --- Custom Help Formatter (for better argparse help output) ---
class CustomHelpFormatter(argparse.HelpFormatter):
    """
    A custom formatter for argparse help output to improve readability and structure.
    This provides slightly more space for arguments and their help text, aligning them.
    """
    def __init__(self, prog, indent_increment=2, max_help_position=30, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)

# --- Argument Parser Setup ---
parser = argparse.ArgumentParser(
    description="Manage materials and templates using POMSicle CLI.",
    formatter_class=CustomHelpFormatter # Apply the custom formatter
)

# --- Argument Groups ---
group_read = parser.add_argument_group("Read Excel File Operations")
group_read.add_argument(
    "--load-materials",
    metavar="[EXCEL_SHEET]",
    help="Specify excel file to create multiple materials at once.",
)
group_read.add_argument(
    "--load-inventory",
    metavar="[EXCEL_SHEET]",
    help="Specify the inventory Excel file to load.",
)

group_create = parser.add_argument_group("Create Single Material Operations")
group_create.add_argument(
    "--create-material", action="store_true", help="Create a material with provided details."
)
group_create.add_argument("-n", metavar="[NAME]", help="Name of a material.")
group_create.add_argument("-d", metavar="[DESCRIPTION]", help="Description of a material.")

group_bom = parser.add_argument_group("BOM Operations")
group_bom.add_argument("--create-bom", action="store_true", help="Create a Bill of Materials (BOM).")

# --- Recipe Template Operations ---
group_template = parser.add_argument_group("Recipe Template Operations")
group_template.add_argument(
    "--create-template",
    nargs='?',
    const='Template.xml',
    metavar="[TEMPLATE_FILE]",
    help="Create a new template from an XML file. Optionally provide the XML filename (e.g., 'MyTemplate.xml'). Defaults to 'Template.xml'.",
)
group_template.add_argument(
    "-rn", "--recipe-name",
    metavar="[RECIPE_NAME]",
    help="Override the default Recipe ID (PM_RECIPE) in the XML template.",
)
group_template.add_argument(
    "-upn", "--unit-procedure-name",
    metavar="[UP_NAME]",
    help="Override the default Unit Procedure ID (PM_SUP) in the XML template.",
)
group_template.add_argument(
    "-opn", "--operation-name",
    metavar="[OP_NAME]",
    help="Override the default Operation ID (PM_OPERATION) in the XML template.",
)


# --- Receiving ---
group_template = parser.add_argument_group("Receiving")
group_template.add_argument(
    "--receive",
    nargs='?',
    const=True,
    metavar="[RECEIVE_OPTION]",
    help="Initiate receiving operation. Optionally provide a value.",
)
group_template.add_argument(
    "-m", "--material-name",
    metavar="[MATERIAL_ID]",
    help="Material ID to receive in POMS.",
)
group_template.add_argument(
    "-u", "--uom",
    metavar="[UOM]",
    help="Material UOM to define.",
)

group_template.add_argument(
    "-c", "--containers",
    metavar="[CONTAINERS]",
    help="Number of containers to receive (default: 1).",
)

group_template.add_argument(
    "-q", "--containers-qty",
    metavar="[CONTAINERS_QTY]",
    help="Quantity per container to receive (default: 1).",
)


# --- Author Info ---
def author_info():
    """Prints author information."""
    author_name = "Hamzza K"
    author_link = "https://hamzza.vercel.app/"
    print('\n' + '-' * 55)
    print(f"Made with ❤  by {author_name} - {author_link}")
    print('-' * 55)

# --- Main Script Logic ---
if __name__ == "__main__":
    logger.info("Checking credentials and attempting login...")
    token_obj = login(username=USERNAME, password=PASSWORD) 
    if not token_obj or not hasattr(token_obj, 'access_token'):
        logger.critical("Initial login failed. Cannot proceed with any operations. Exiting.")
        exit(1)
    logger.info("Initial login successful.")

    args = parser.parse_args()

    if args.create_template is not None:
        template_xml_filename = args.create_template
        recipe_name = args.recipe_name
        unit_procedure_name = args.unit_procedure_name
        operation_name = args.operation_name

        # If only recipe name is provided, auto-fill others
        if recipe_name and not unit_procedure_name and not operation_name:
            logger.info(f"Only Recipe Name ('{recipe_name}') provided. Auto-filling UP and OP names.")
            unit_procedure_name = f"{recipe_name}_UP"
            operation_name = f"{recipe_name}_OP"
        
        logger.debug(f"Attempting to create template using XML file: '{template_xml_filename}'")
        if recipe_name:
            logger.debug(f"Recipe Name: {recipe_name}")
        if unit_procedure_name:
            logger.debug(f"Unit Procedure Name: {unit_procedure_name}")
        if operation_name:
            logger.debug(f"Operation Name: {operation_name}")
        
        try:
            template_manager = PomsicleTemplateManager(settings, USERNAME, PASSWORD)
            success = template_manager.create_template(
                template_name=template_xml_filename,
                recipe_name=recipe_name,
                unit_procedure_name=unit_procedure_name,
                operation_name=operation_name
            )
            if success:
                logger.info(f"'{template_xml_filename}' operation completed successfully.")
            else:
                logger.error(f"'{template_xml_filename}' operation failed.")
                Banner.error(f"'{template_xml_filename}' operation failed.")
        except ValueError as e:
            logger.critical(f"Failed to initialize Template Manager: {e}")
            exit(1)
        except Exception as e:
            logger.critical(f"An unexpected error occurred during template creation: {e}")
            exit(1)

    elif args.load_inventory:
        logger.info(f"Loading inventory from: {args.load_inventory}")
        read_inventory(token=token_obj.access_token, filename=args.load_inventory)
    elif args.create_material:
        if args.n and args.d:
            logger.info(f"Creating material with name: '{args.n}' and description: '{args.d}'")
        else:
            logger.error("Error: Both name (-n) and description (-d) are required for creating a material.")
            parser.print_help()
    elif args.load_materials:
        ban.error("Loading materials functionality under development!")
        logger.warning(f"Loading materials from: {args.load_materials} (Functionality under development)")
    elif args.create_bom:
        logger.info("Creating BOM.")

    elif args.receive:
        if args.material_name and args.uom:
            logger.info(f"Receiving material: '{args.material_name}' with UOM: '{args.uom}'")
            try:
                receive_manager = ReceiveManager(settings, receive_settings, USERNAME, PASSWORD)
                success = receive_manager.receive(
                    material_name=args.material_name,
                    uom=args.uom,
                    containers=args.containers if args.containers else 1,
                    qty_per_container=args.containers_qty if args.containers_qty else 1
                )
                if success:
                    ban.success(f"Material '{args.material_name}' received successfully.")
                else:
                    logger.error(f"Failed to receive material '{args.material_name}'.")
            except ValueError as e:
                logger.critical(f"Failed to initialize Receive Manager: {e}")
                exit(1)
            except Exception as e:
                logger.critical(f"An unexpected error occurred during material receiving: {e}")
                exit(1)
        else:
            logger.error("Error: Both material name (-m) and UOM (-u) are required for receiving a material.")
            parser.print_help()
    else:
        logger.info("No valid option provided. Use --help for available commands.")
        parser.print_help()

    author_info()