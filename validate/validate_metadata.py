#! /usr/bin/python

import csv
import json
import jsonschema

schemafile = 'AMC_v0.8.p5.json'
with open(schemafile, "r") as read_file:
    schema = json.load(read_file)

jsonschema.Draft7Validator.check_schema(schema)

fileID = 'metadata_test2' 
filetsv = fileID + '.tsv'
filejson = fileID + '.json'

v = jsonschema.Draft7Validator(schema)

with open(filetsv) as tsvfile:
  reader = csv.DictReader(tsvfile, dialect='excel-tab')
  # skip TYPE row
  next(reader)
  for row in reader:
    print(row['disease'])
    for error in v.iter_errors(row):
        print(row['NAME'], "error:", error.message)