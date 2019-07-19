#! /usr/bin/python

"""Validate input metadata tsv file against metadata convention

DESCRIPTION
This CLI takes a tsv metadata file and validates against a metadata convention
using the python jsonschema library. The metadata convention JSON schema
represents the rules that should be enforced on metadata files for studies
participating under the convention.

EXAMPLE
# Using json file for Alexandria metadata convention tsv, validate input tsv
$ validate_metadata.py AMC_v0.8.json metadata_test.tsv

"""

import csv
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
    parser.add_argument('--output', '-o', type=str,
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
            if not value:
                row[key] = None
            if array_format.match(value):
                row[key] = json.loads(value)
            if type[key] == "numeric":
                try:
                  row[key] = float(value)
                except:
                  pass
            
        for error in v.iter_errors(row):
            print(row['NAME'], "error:", error.message)
#        print(row)