# pomsicle.py (Your main CLI entry script)

import argparse
import logging
from banners import Banner
from inventory.read_inventory import read_file as read_inventory
from credentials import login
from config import config

# Import the new class from the template module
from template.template import PomsicleTemplateManager # Adjust path as needed

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Global Configuration ---
try:
    settings = config(translator='pomsicle')
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

group_template = parser.add_argument_group("Recipe Template Operations")
group_template.add_argument(
    "--create-template",
    nargs='?',
    const='Template.xml',
    metavar="[TEMPLATE_FILE]",
    help="Create a new template from an XML file. Optionally provide the XML filename (e.g., 'MyTemplate.xml'). Defaults to 'Template.xml'.",
)

# --- Author Info ---
def author_info():
    """Prints author information."""
    author_name = "Hamzza K"
    author_link = "https://hamzza.vercel.app/"
    print('\n' + '-' * 55)
    print(f"Made with ❤  by {author_name} - {author_link}")
    print('-' * 55)

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
        logger.info(f"Attempting to create template using XML file: '{template_xml_filename}'")
        
        try:
            template_manager = PomsicleTemplateManager(settings, USERNAME, PASSWORD)
            success = template_manager.create_template(template_name=template_xml_filename)
            if success:
                logger.info(f"Template '{template_xml_filename}' operation completed successfully.")
            else:
                logger.error(f"Template '{template_xml_filename}' operation failed.")
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
            # This is where you would call your Material creation logic
            # e.g., PomsicleMaterialManager(settings, USERNAME, PASSWORD).create_material(args.n, args.d)
        else:
            logger.error("Error: Both name (-n) and description (-d) are required for creating a material.")
            parser.print_help()
    elif args.load_materials:
        ban.error("Loading materials functionality under development!")
        logger.warning(f"Loading materials from: {args.load_materials} (Functionality under development)")
    elif args.create_bom:
        logger.info("Creating BOM.")
    else:
        logger.info("No valid option provided. Use --help for available commands.")
        parser.print_help()

    author_info()