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
from collections import defaultdict


class Cell_Metadata:
    def __init__(self, file_path):
        self.file = open(file_path, 'r')
        self.headers = self.file.readline().rstrip('\n').split("\t")
        self.metadata_types = self.file.readline().rstrip('\n').split("\t")
        self.annotation_type = ['group', 'numeric']
        self.errors = defaultdict(list)

    def validate_format(self):
        if not self.headers[0] == 'NAME':
            self.errors['format'].append(
                ('Error: Metadata file header row malformed, missing NAME')
            )
            valid = False
        else:
            self.headers.remove('NAME')
        if not self.metadata_types[0] == 'TYPE':
            self.errors['format'].append(
                ('Error: Metadata file TYPE row malformed, missing TYPE')
            )
            valid = False
        else:
            self.metadata_types.remove('TYPE')
        annot_err = False
        annots = []
        for t in self.metadata_types:
            if t not in self.annotation_type:
                annots.append(t)
                annot_err = True
        if annot_err:
            self.errors['format'].append(
                (
                    'Error: TYPE declarations should be "group" or "numeric";'
                    'please correct {annots}'.format(annots=annots)
                )
            )
            valid = False
        if not len(self.headers) == len(self.metadata_types):
            self.errors['format'].append(
                str(
                    'Error: {x} TYPE declarations for {y} column headers'.
                    format(
                        x=len(self.headers) - 1, y=len(self.metadata_types) - 1
                    )
                )
            )
            valid = False
        return valid


def create_parser():
    """
    Parse command line values for validate_metadata

    """
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Output file name [optional]',
        default=None
    )
    parser.add_argument(
        'convention', type=str, help='Metadata convention json file [Required]'
    )
    parser.add_argument('input_metadata', help='Metadata tsv file [Required]')
    return parser


def load_schema(schemafile):
    """
    Read Convention
    :param schemafile: metadata convention file
    :return: dict representing metadata convention
    """
    with open(schemafile, "r") as read_file:
        schema = json.load(read_file)


# ToDo - action if schema is invalid?
    jsonschema.Draft7Validator.check_schema(schema)
    valid_schema = jsonschema.Draft7Validator(schema)

    return valid_schema
"""
Read tsv input row by row
"""
"""
ontology validation
"""
"""
generate error report
"""
"""
WAIT: handle array data types

"""
"""
DEFER (loom): Check loom format is valid
  what are the criteria?
"""
"""
DEFER (loom): Read loom metadata, row by row?
"""
"""
DEFER: Things to check before pass intended data types to FireStore
ensure numeric (TYPE == numeric in tsv; type number or integer in loom)
    stored as numeric
ensure group (even if it is a number) stored as string
NaN stored as null?
error on empty cells
"""
"""

"""

if __name__ == '__main__':
    args = create_parser().parse_args()
    schema = load_schema(args.convention)

    # filetsv = 'metadata_test3.tsv'
    filetsv = args.input_metadata
    metadata = Cell_Metadata(filetsv)
    print('Validating', filetsv)
    metadata.validate_format()
    # printing errors below is broken - need getter for errors?
    # for error in metadata.errors['format']':
    #     print("error:", error)
    print("error:", metadata.errors.items())

    # compiled regex to identify arrays in metadata file
    array_format = re.compile(r'\[.*\]')

    with open(filetsv) as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        # skip TYPE row
        type = next(reader)
        for row in reader:
            #    print(row['NAME'], row['disease'])
            # DictReader values are strings
            #   reformat all intended arrays from string
            # TODO replace empty values with NONE?
            #   or other handling for empties
            for key, value in row.items():
                if not value:
                    row[key] = None
                if array_format.match(value):
                    row[key] = json.loads(value)
                if type[key] == "numeric":
                    try:
                        row[key] = float(value)
                    # terrible antipattern below - must fix
                    except Exception:
                        pass

            for error in schema.iter_errors(row):
                print(row['NAME'], "error:", error.message)
#        print(row)
