import argparse
from banners import Banner
from bom.bom_mapper import Header
from inventory.inventory_payload import Payload
from config.credentials import login
import getpass

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

parser = argparse.ArgumentParser(description="create/load materials using POMSicle")

group_read = parser.add_argument_group("Read Excel File")
group_create = parser.add_argument_group("Create a single material")
group_bom = parser.add_argument_group("Create BOM")

group_read.add_argument(
    "--load-materials",
    metavar="[Excel Sheet]",
    help="Specify excel file to create multiple materials at once.",
)
group_read.add_argument(
    "--load-inventory",
    metavar="[Excel Sheet]",
    help="Specify the inventory Excel file to load.",
)

group_create.add_argument(
    "--create-material", action="store_true", help="Create a material"
)
group_create.add_argument("-n", metavar="[name]", help="Name of a material")
group_create.add_argument("-d", metavar="[description]", help="Description of a material")

group_bom.add_argument("--create-bom", action="store_true", help="Create a BOM")

def author():
    author_name = "Hamzza K"
    author_link = "https://hamzza.vercel.app/"
    print('\n-----------------------------------------------------')
    print(f"Made with ❤  by {author_name} - {author_link}")
    print('-----------------------------------------------------')


try:
    args = parser.parse_args()
except SystemExit:
    parser.print_help()
    author()
    exit(1)

print("Please enter your credentials\n")
username = input("Username: ")
password = getpass.getpass("Password: ")
print("Checking credentials...")
login(username=username, password=password)

args = parser.parse_args()

# Handling --read-file
if args.read_file:
    ban.info(f"Reading: {args.read_file}")
    # read_file(args.read_file)

# Handling --load-inventory
elif args.load_inventory:
    ban.info(f"Loading inventory from: {args.load_inventory}")

# Handling --create-material
elif args.create_material:
    if args.n and args.d:
        print("Creating material with name:", args.n, "and description:", args.d)
    else:
        print(
            "Error: Both name (-n) and description (-d) are required for creating material."
        )

# Handling --create-bom
elif args.create_bom:
    print("Creating BOM")

# No valid options provided
else:
    print(
        "No valid options provided. Use --read-file, --load-inventory, or --create-material."
    )
    author()
