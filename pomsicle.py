#!/usr/bin/env python3
# Author: Hamzza K

import os
import sys
import argparse
import logging

from banners import Banner
from bom.bom_template import PomsicleBOMManager
from inventory.read_inventory import read_file as read_inventory
from credentials import login
from config import config
from receive.receiving import ReceiveManager
from recipe.builder import RecipeBuilder
from template.recipe_template import PomsicleTemplateManager

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def get_script_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

script_directory = get_script_dir()
config_folder_name = 'config'
config_file_name = 'config.cfg'

# -----------------------------------------------------------------------------
# Load Config
# -----------------------------------------------------------------------------
try:
    settings = config(translator='pomsicle')
    receive_settings = config(translator='pomsicle:receive')
except (FileNotFoundError, ValueError) as e:
    logger.critical(f"Configuration error: {e}. Exiting.")
    exit(1)

USERNAME = settings.get('USERNAME')
PASSWORD = settings.get('PASSWORD')

# -----------------------------------------------------------------------------
# Banner
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# Subcommand Handler Functions
# -----------------------------------------------------------------------------

# pomsicle template create
def handle_template_create(args, token):
    template_xml = args.template_file
    recipe_name = args.recipe_name
    up_name = args.unit_procedure_name
    op_name = args.operation_name

    if recipe_name and not (up_name or op_name):
        logger.info(f"Auto-generating UP/OP names from recipe '{recipe_name}'.")
        up_name = f"{recipe_name}_UP"
        op_name = f"{recipe_name}_OP"

    try:
        manager = PomsicleTemplateManager(settings, USERNAME, PASSWORD)
        ok = manager.create_template(
            template_name=template_xml,
            recipe_name=recipe_name,
            unit_procedure_name=up_name,
            operation_name=op_name,
        )

        if ok:
            logger.info(f"Template '{template_xml}' created successfully.")
        else:
            logger.error(f"Template '{template_xml}' failed.")
    except Exception as e:
        logger.critical(f"Template creation failed: {e}")
        exit(1)

# pomsicle inventory load
def handle_inventory_load(args, token):
    logger.info(f"Loading inventory: {args.file}")
    read_inventory(token=token.access_token, filename=args.file)

# pomsicle receiving start
def handle_receiving_start(args, token):
    if not args.material or not args.uom:
        logger.error("Material and UOM required.")
        exit(1)

    try:
        rm = ReceiveManager(settings, receive_settings, USERNAME, PASSWORD)
        ok = rm.receive(
            material_name=args.material,
            uom=args.uom,
            containers=args.containers,
            qty_per_container=args.qty
        )

        if ok:
            ban.success(f"Material '{args.material}' received successfully.")
        else:
            logger.error(f"Failed receiving '{args.material}'.")
    except Exception as e:
        logger.critical(f"Receiving failed: {e}")
        exit(1)


def handle_recipe_create_template(args, token=None):
    logger.info(f"Creating RECIPE from built-in template: {args.template_name}")

    template_xml_filename = args.template_name 
    recipe_name = args.recipe_name
    unit_procedure_name = args.unit_procedure if args.unit_procedure else None
    operation_name = args.operation if args.operation else None

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
            logger.debug(f"'{template_xml_filename}' operation completed successfully.")
        else:
            logger.error(f"'{template_xml_filename}' operation failed.")
            Banner.error(f"'{template_xml_filename}' operation failed.")
    except ValueError as e:
        logger.critical(f"Failed to initialize Template Manager: {e}")
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred during template creation: {e}")
        exit(1)

def handle_bom_start(args, token=None):
    logger.info(f"Starting BOM process for: {args.template_name}")
    # Implement BOM start logic here

    try:
        template_manager = PomsicleBOMManager(settings, USERNAME, PASSWORD)
        success = template_manager.create_template(
            template_name=args.template_name,
            recipe_name=None,
            unit_procedure_name=None,
            operation_name=None
        )
        if success:
            logger.debug(f"BOM '{args.template_name}' operation completed successfully.")
        else:
            logger.error(f"BOM '{args.template_name}' operation failed.")
            Banner.error(f"BOM '{args.template_name}' operation failed.")
    except ValueError as e:
        logger.critical(f"Failed to initialize Template Manager: {e}")
        exit(1)


def handle_recipe_create_custom(args, token=None):
    builder = RecipeBuilder()
    args.template_name = "Assisted.xml"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(current_dir, "template")
    output_file = os.path.join(template_folder, args.template_name)
    args.unit_procedure = None 
    args.operation = None

    logger.info(f"Creating CUSTOM RECIPE with phases: {args.add}")
    builder.insert_components(args.add, output_file)
    logger.info(f"Custom recipe created with: {' → '.join(args.add)}")

    handle_recipe_create_template(args, token=None)


def handle_recipe_import(args, token=None):
    logger.info(f"Importing recipe from: {args.filename}")
    print(f"Imported recipe from: {args.filename}")


# -----------------------------------------------------
# CLI Setup (subcommands)
# -----------------------------------------------------
def create_cli():
    parser = argparse.ArgumentParser(prog="pomsicle", description="POMSicle CLI")

    subparsers = parser.add_subparsers(dest="command")

    # ================================
    # pomsicle recipe
    # ================================
    recipe_create = subparsers.add_parser("recipe", help="Create recipe")
    recipe_create_sub = recipe_create.add_subparsers(dest="create_type")

    # ----- pomsicle recipe create template -----
    create_template = recipe_create_sub.add_parser("template", help="Create recipe using built-in template")
    create_template.add_argument("recipe_name", help="Name of the recipe.")
    create_template.add_argument("--unit-procedure", help="Name of the unit procedure.")
    create_template.add_argument("--operation", help="Name of the operation.")
    create_template.add_argument("--template-name", default="Template.xml", help="Name of the template.")
    create_template.set_defaults(func=handle_recipe_create_template)

    # ----- pomsicle recipe create custom -----
    create_custom = recipe_create_sub.add_parser("custom", help="Create a custom recipe")
    create_custom.add_argument("--recipe-name", default="Assisted", help="Name of the recipe.")
    create_custom.add_argument(
        "--add",
        nargs="+",
        required=True,
        help="List of objects to add into the custom recipe"
    )
    create_custom.set_defaults(func=handle_recipe_create_custom)

    # -------------------------------------------------------
    # pomsicle recipe import <filename>
    # -------------------------------------------------------
    recipe_import = subparsers.add_parser("import", help="Import recipe from XML")
    recipe_import.add_argument("filename", help="XML file to import")
    recipe_import.set_defaults(func=handle_recipe_import)
    # ================================
    # pomsicle inventory
    # ================================
    inventory = subparsers.add_parser("inventory", help="Inventory operations")
    inv_sub = inventory.add_subparsers(dest="action")

    load = inv_sub.add_parser("load", help="Load inventory from Excel")
    load.add_argument("file", help="Excel file")
    load.set_defaults(func=handle_inventory_load)

    # ================================
    # pomsicle receiving
    # ================================
    receiving = subparsers.add_parser("receiving", help="Receiving operations")
    r_sub = receiving.add_subparsers(dest="action")

    start = r_sub.add_parser("start", help="Start receiving material")
    start.add_argument("--material", "-m", required=True)
    start.add_argument("--uom", "-u", required=True)
    start.add_argument("--containers", "-c", type=int, default=1)
    start.add_argument("--qty", "-q", type=float, default=1)
    start.set_defaults(func=handle_receiving_start)

    # ================================
    # pomsicle bom
    # ================================
    bom = subparsers.add_parser("bom", help="BOM operations")
    b_sub = bom.add_subparsers(dest="action")

    start = b_sub.add_parser("start", help="Start BOM process")
    start.add_argument("--template-name", default="Bom_template.xml", help="BoilerPlate recipe.")
    start.set_defaults(func=handle_bom_start)

    return parser

# -----------------------------------------------------------------------------
# Author Info
# -----------------------------------------------------------------------------
def author_info():
    print("\n" + "-" * 55)
    print("Made with ❤  by Hamzza K - https://hamzza.vercel.app/")
    print("-" * 55)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Authenticating...")
    token_obj = login(username=USERNAME, password=PASSWORD)

    if not token_obj or not hasattr(token_obj, "access_token"):
        logger.critical("Login failed. Exiting.")
        exit(1)

    parser = create_cli()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        exit(0)

    args.func(args, token_obj)
    author_info()
