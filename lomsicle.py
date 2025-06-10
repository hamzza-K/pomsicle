import argparse
import logging
from banners import Banner
from inventory.read_inventory import read_file as read_inventory
from credentials import login
from config import config

# --- Logging Configuration ---
# Basic logging setup for general output, not directly for argparse help formatting
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

# --- Helper Function for Template Creation (Placeholder) ---
def create_template_action(username: str, password: str, template_name: str = "NewTemplate"):
    """
    Placeholder function for creating a template.
    This is where your actual API call to create the template would go.
    """
    logger.info(f"Initiating template creation:")
    logger.info(f"  Template Name: {template_name}")
    logger.info(f"  Using User:    {username}")
    logger.debug(f"  (Password for API call: {password[:2]}...{password[-2:]})") # Mask password
    # Your actual API call to POMSicle for template creation would be implemented here.
    # For example:
    # try:
    #     session = requests.Session()
    #     auth_token = login(username=username, password=password).access_token # Assuming login returns an object with access_token
    #     headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    #     template_api_url = f"{settings.get('BASE_APP_URL')}TemplateService/CreateTemplate" # Example URL
    #     payload = {"name": template_name, "createdBy": username}
    #     response = session.post(template_api_url, headers=headers, json=payload, verify=False)
    #     response.raise_for_status()
    #     logger.info(f"Successfully sent request to create template '{template_name}'. Server response: {response.json()}")
    # except Exception as e:
    #     logger.error(f"Error creating template '{template_name}': {e}")
    logger.info(f"Template creation logic for '{template_name}' would be executed now.")

# --- Custom Help Formatter (Optional but enhances readability) ---
class CustomHelpFormatter(argparse.HelpFormatter):
    """
    A custom formatter for argparse help output to improve readability.
    This provides slightly more space for arguments and their help text.
    For more complex tabular output, consider 'rich' or a more advanced formatter.
    """
    def __init__(self, prog, indent_increment=2, max_help_position=30, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)

# --- Argument Parser Setup ---
# Using the custom formatter
parser = argparse.ArgumentParser(
    description="Manage materials and templates using POMSicle CLI.",
    formatter_class=CustomHelpFormatter # Apply the custom formatter here
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

# --- New Argument Group: Create Template ---
group_template = parser.add_argument_group("Template Operations")
group_template.add_argument(
    "--create-template",
    nargs='?',                 # Makes the argument optional
    const='DefaultTemplate',   # Value if --create-template is present but no name given
    metavar="[TEMPLATE_NAME]", # How it appears in help message
    help="Create a new template. Optionally provide a custom name.",
)

# --- Author Info ---
def author_info():
    """Prints author information."""
    author_name = "Hamzza K"
    author_link = "https://hamzza.vercel.app/"
    print('\n' + '-' * 50)
    print(f"Made with ❤ by {author_name} - {author_link}")
    print('-' * 50)

# --- Main Script Logic ---
if __name__ == "__main__":
    ban = Banner()
    print(r"""
 ________   ________    _____ ______     ________       ___      ________       ___           _______
|\  __  \  |\  __  \   |\  _ \  _  \   |\  ____\      |\  \    |\  ____\     |\  \           |\  ___ \
\ \  \|\  \ \ \  \|\  \  \ \  \\\__\ \  \  \ \  \___|_    \ \  \    \ \  \___|     \ \  \           \ \  __/|
 \ \  ____\ \ \  \\\  \  \ \  \\|__| \  \  \ \_____  \     \ \  \    \ \  \         \ \  \           \ \  \_|/__
  \ \ \___|  \ \  \\\  \  \ \  \    \ \  \  \|____|\  \     \ \  \    \ \  ____     \ \  ____     \ \ \_|\ \
   \ \__\      \ \_______\  \ \__\    \ \__\   ____\_\  \     \ \__\    \ \_______\   \ \_______\   \ \_______\
    \|__|       \|_______|   \|__|     \|__|  |\_________|     \|__|     \|_______|    \|_______|    \|_______|
                                               \|_________|
""")
    
    logger.info("Checking credentials...")
    token = login(username=USERNAME, password=PASSWORD) # Ensure your login returns an object with access_token

    if not token or not hasattr(token, 'access_token'):
        logger.critical("Login failed. Could not retrieve access token. Exiting.")
        exit(1)
    logger.info("Login successful.")

    args = parser.parse_args()

    if args.create_template is not None:
        template_name_to_create = args.create_template
        create_template_action(USERNAME, PASSWORD, template_name_to_create)
    elif args.load_inventory:
        logger.info(f"Loading inventory from: {args.load_inventory}")
        read_inventory(token=token.access_token, filename=args.load_inventory)
    elif args.create_material:
        if args.n and args.d:
            logger.info(f"Creating material with name: '{args.n}' and description: '{args.d}'")
        else:
            logger.error("Error: Both name (-n) and description (-d) are required for creating a material.")
            parser.print_help() # Show help if required args are missing
    elif args.load_materials:
        ban.error("Loading materials functionality under development!")
        logger.warning(f"Loading materials from: {args.load_materials} (Functionality under development)")
        # read_file(args.load_materials) # Uncomment if 'read_file' is used here
    elif args.create_bom:
        logger.info("Creating BOM.")
    else:
        logger.info("No valid option provided. Use --help for available commands.")
        parser.print_help() # Show help if no valid option is given

    author_info()