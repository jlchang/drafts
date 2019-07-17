#! /usr/bin/python

import csv
#! /usr/bin/python

import argparse
import re
import json
import jsonschema


def create_parser():
    """
    Command Line parser for validate_metadata

    Inputs: metadata convention and metadata tsv files
    """
    # create the argument parser
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # add arguments
    parser.add_argument('--output', '-0', type=str,
                        help='Output file name [optional]', default=None)
    parser.add_argument('convention', type=str,
                        help='Metadata convention json file [Required]')
    parser.add_argument('input_metadata',
                        help='Metadata tsv file [Required]')
    return parser

if __name__ == '__main__':
    args = create_parser().parse_args()


    schemafile = args.convention
    with open(schemafile, "r") as read_file:
        schema = json.load(read_file)

    jsonschema.Draft7Validator.check_schema(schema)

    # filetsv = 'metadata_test3.tsv'
    filetsv = args.input_metadata

    v = jsonschema.Draft7Validator(schema)

    # compiled regex to identify arrays in metadata file
    array_format = re.compile('\[.*\]')

    with open(filetsv) as tsvfile:
      reader = csv.DictReader(tsvfile, dialect='excel-tab')
      # skip TYPE row
      type = next(reader)
      for row in reader:
    #    print(row['NAME'], row['disease'])
        # DictReader values are strings: reformat all intended arrays from string
        # TODO replace empty values with NONE? or other handling for empties
        for key, value in row.items():
            if array_format.match(value):
                row[key] = json.loads(value)
            if type[key] == "numeric":
                try:
                  row[key] = float(value)
                except:
                  pass
        for error in v.iter_errors(row):
            print(row['NAME'], "error:", error.message)
    #    print(row)