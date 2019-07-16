#! /usr/bin/python

import argparse
import csv
import os
import json
import re

"""Produce JSON Schema from metadata convention tsv file

DESCRIPTION
This CLI takes a tsv metadata convention and creates a JSON Schema representation.
The JSON schema represents the rules that should be enforced on metadata files 
for studies participating under the convention.

EXAMPLE
# Generate json file for Alexandria from the Alexandria metadata convention tsv
$ python serialize_convention.py Alexandria AMC_20190618_test_v7.tsv 

"""

__author__ = "Jean Chang"
__copyright__ = "Copyright 2019"
__license__ = "MIT"
__email__ = "jlchang@broadinstitute.org"
__status__ = "Development"


def create_parser():
    """
    Command Line parser for serialize_convention

    Input: metadata convention tsv file
    """
    # create the argument parser
    parser = argparse.ArgumentParser(
        description='Produce JSON Schema from metadata convention tsv file.',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # add arguments
    parser.add_argument('collective', type=str,
                        help='name of the project that the metadata ' +
                        'convention belongs to [Required]')
    parser.add_argument('input_convention',
                        help='Metadata convention tsv file')
    parser.add_argument('--label', '-l', type=str,
                        help='Label to insert into the file name ' +
                        'for the Metadata convention json file [optional]',
                        default=None),
    parser.add_argument('--output_file', '-o', type=str,
                        help='Output file name [optional]', default=None)
    return parser


def add_dependency(key, value, dict):
    """
    Add dependency to appopriate dictionary

    ToDo: check if defaultdict would eliminate this function
    """
    if key in dict:
        if value not in dict[key]:
            dict[key].append(value)
    else:
        dict[key] = [value]


def build_array_object(row):
    """
    Build "items" dictionary object according to Class type
    """
    dict = {}
    # handle time attributes as string with time format
    if row['class'] == 'time':
        dict['type'] = row['type']
        dict['format'] = row['class']
        print('dict time', dict, 'for', row['attribute'])
        return dict
    # handle controlled-list attributes as enum
    elif row['class'] == 'enum':
        dict['type'] = row['type']
        dict[row['class']] = row['controlled_list_entries']
        print('dict enum', dict, 'for', row['attribute'])
        return dict
    else:
        dict['type'] = row['type']
        return dict


def build_single_object(row, dict):
    """
    Add appropriate class properties for non-array attributes
    """
    # handle time attributes as string with time format
    if row['class'] == 'time':
        dict['type'] = row['type']
        dict['format'] = row['class']
        print('single time', dict, 'for', row['attribute'])

    # handle controlled-list attributes as enum
    elif row['class'] == 'enum':
        dict['type'] = row['type']
        dict[row['class']] = row['controlled_list_entries']
        print('single enum', dict, 'for', row['attribute'])

    else:
        dict['type'] = row['type']


def build_schema_info(collective):
    """
    generate dictionary of schema info for the collective
    """
    info = {}
    info['$schema'] = 'http://json-schema.org/draft-07/schema#'
    info['$id'] = ('http://singlecell.broadinstitute.org/schemas/'
                   '%s.schema.json' % (collective))
    info['title'] = collective + ' Metadata Convention'
    info['description'] = ('Metadata convention for the '
                           '%s project' % (collective))
    return info


def dump_json(dict, filename):
    """
    write metadata convention json file
    """
    with open(filename, 'w') as jsonfile:
        json.dump(dict, jsonfile, sort_keys=True, indent=4)
    jsonfile.close()
    print("end dump_json")


def clean_json(filename):
    """
    remove escape characters to produce proper JSON Schema format
    """
    with open(filename, 'r') as jsonfile:
        jsonstring = jsonfile.read()
        jsonstring = re.sub(r'"\[', r'[', jsonstring)
        jsonstring = re.sub(r'\]"', r']', jsonstring)
        jsonstring = re.sub(r'\\"', r'"', jsonstring)
    jsonfile.close()
    return jsonstring


def write_json_schema(filename, object):
    """
    write JSON Schema file
    """
    with open(filename, 'w') as jsonfile:
        jsonfile.write(object)
    print("end write_json_schema")


def generate_output_name(inputname, label):
    """
    Build output filename from inputname
    """
    head, tail = os.path.split(inputname)
    name, suffix = os.path.splitext(tail)
    if label:
        labeledName = '.'.join([name, label, 'json'])
    else:
        labeledName = '.'.join([name, 'json'])
    if head:
        outputname = '/'.join([head, labeledName])
    else:
        outputname = labeledName
    return outputname


def serialize_convention(convention, input_convention):
    """
    Build convention as a Python dictionary
    """

    properties = {}
    required = []
    dependencies = {}

    with open(input_convention) as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')

        for row in reader:
            entry = {}

            # build list of required attributes for metadata convention schema
            if row['required']:
                required.append(row['attribute'])

            # build dictionary of dependencies for metadata convention schema
            if row['dependency']:
                # dependencies (aka "if" relationships) are uni-directional
                # if 'attribute', 'dependency' must also exist
                add_dependency(
                    row['attribute'], row['dependency'], dependencies)
            if row['dependent']:
                # dependent is bi-directional (aka "required-if")
                add_dependency(row['attribute'], row['dependent'], dependencies)
                add_dependency(row['dependent'], row['attribute'], dependencies)

            # build dictionary for each attribute
            if row['default']:
                entry['default'] = row['default']
            if row['attribute_description']:
                entry['description'] = row['attribute_description']

            # handle properties unique to the ontology class of attributes
            if row['class'] == 'ontology':
                entry[row['class']] = row['ontology']
                entry['ontology_root'] = row['ontology_root']

            # handle arrays of values
            if row['array']:
                entry['type'] = 'array'
                entry['items'] = build_array_object(row)
            else:
                build_single_object(row, entry)

            if row['dependency_condition']:
                entry['dependency_condition'] = row['dependency_condition']

            # build dictionary of properties for the metadata convention schema
            properties[row['attribute']] = entry

        # build metadata convention schema
        convention['properties'] = properties
        convention['required'] = required
        convention['dependencies'] = dependencies

    tsvfile.close()
    return convention


def write_schema(dict, inputname, label, filename):
    if filename:
        filename = generate_output_name(filename, label)
    else:
        filename = generate_output_name(inputname, label)
    dump_json(dict, filename)
    write_json_schema(filename, clean_json(filename))


if __name__ == '__main__':
    args = create_parser().parse_args()
    input_convention = args.input_convention
    label = args.label
    output_file = args.output_file
    collective = args.collective
    schemaInfo = build_schema_info(collective)
    convention = serialize_convention(schemaInfo, input_convention)
    write_schema(convention, input_convention, label, output_file)
