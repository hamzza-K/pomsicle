import argparse
from MaterialMaster import record_look_up, header_look_up
from pomstransaction import POMSTransactionXML, POMSTransactionJSON

parser = argparse.ArgumentParser()

parser.add_argument('-j', '--json', action='store_true',
                     help="Returns the material file in JSON format.")
parser.add_argument('-x', '--xml', action='store_true',
                     help='Returns the material file in XML format. ')
parser.add_argument('-n', '--name', required=True, help='Name of the material.')
parser.add_argument('-d', '--desc', help='Description of the material.')
parser.add_argument('-o', '--output', help='Output file name of the material.')

args = parser.parse_args()

description = args.desc if args.desc else args.name

poms_transaction = POMSTransactionXML() if args.xml else POMSTransactionJSON()

# Add the Header
for k, v in header_look_up.items():
    poms_transaction.add_header(v, k)

# Add the Records
for k, v in record_look_up.items():
    poms_transaction.add_record(v, k)

poms_transaction.add_record("MaterialID", args.name)
poms_transaction.add_record("MaterialDescription", description)

print(poms_transaction.to_string())

EXT = 'xml' if args.xml else 'json'
poms_transaction.save(f'{args.output}.{EXT}')




