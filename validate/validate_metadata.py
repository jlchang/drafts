#! /usr/bin/python

import csv
import re
import json
import jsonschema

schemafile = 'AMC_v0.8.p5.json'
with open(schemafile, "r") as read_file:
    schema = json.load(read_file)

jsonschema.Draft7Validator.check_schema(schema)

#fileID = 'metadata_test3'
fileID = 'error_test3' 
filetsv = fileID + '.tsv'
filejson = fileID + '.json'

v = jsonschema.Draft7Validator(schema)

# compiled regex to identify arrays in metadata file
array_format = re.compile('\[.*\]')

with open(filetsv) as tsvfile:
  reader = csv.DictReader(tsvfile, dialect='excel-tab')
  # skip TYPE row
  next(reader)
  for row in reader:
#    print(row['NAME'], row['disease'])
    # DictReader values are strings: reformat all intended arrays from string
    # TODO replace empty values with NONE? or other handling for empties
    for key, value in row.items():
        if array_format.match(value):
            row[key] = json.loads(value)
    for error in v.iter_errors(row):
        print(row['NAME'], "error:", error.message)
#    print(row)