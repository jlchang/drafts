"""bq_facet_filter_fixes.py

DESCRIPTION
Open a file with an annotated Mongo query result, find outdated ontology labels, output BQ commands to update

EXAMPLE
python bq_facet_filter_fixes.py <input file>

Input file is result of this Mongoid query of the SCP production database:

facets = SearchFacet.where(is_ontology_based: true)
facets.each do |facet|
    facet.filters_with_external.each do |f|
        print facet.big_query_id_column, "|", f.to_json, "\n"
    end
 end

orig file: /Users/jlchang/Documents/Broad/SCP/cb_work/2022/facet_filter_cleanup/prod_filters_20220111

"""

import argparse
import json
from validate_metadata import (
    OntologyRetriever,
    MAX_HTTP_REQUEST_TIME,
    MAX_HTTP_ATTEMPTS,
#add "has_narrow_synonym" to Ontology Retriever

def create_parser():
    """Parse command line values
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("input", help="input file")
    return parser


if __name__ == "__main__":
    args = create_parser().parse_args()
    arguments = vars(args)

    # setup to use Ontology Retriever
    retriever = OntologyRetriever()
    convention_url = "/Users/jlchang/Documents/GitHub/scp-ingest-pipeline/schema/alexandria_convention/alexandria_convention_schema.json"
    with open(convention_url, "r") as f:
        convention = json.load(f)

    with open(args.input, "r") as file:
        lines = file.readlines()

    results = [line.rstrip("\n") for line in lines]
    old_facet = ""
    azul_filters = []
    for r in results:
        facet_name, filter_info = r.split("|")
        if old_facet != facet_name:
            print(f"*** {facet_name}")
            old_facet = facet_name
        filter = json.loads(filter_info)
        # print(f'{filter["id"]} {filter["name"]}')
        if facet_name != "organ_region":
            if filter["id"] == filter["name"]:
                # print(f'     skipping Azul filter {filter["id"]}')
                azul_filters.append((facet_name, filter["name"]))
            else:
                # print(f'  compare EBI OLS for {filter["id"]} with {filter["name"]}')
                label_and_synonyms = retriever.retrieve_ontology_term_label_and_synonyms(
                    filter["id"], facet_name, convention, "ontology"
                )
                label = label_and_synonyms.get("label")
                synonyms = label_and_synonyms.get("synonyms")
                if filter["name"] == label:
                    # print(f'  No change: {filter["name"]} is current label')
                    pass
                elif filter["name"].casefold() == label.casefold():
                    print(f'CASE update: {filter["name"]} -> {label}')
                elif synonyms:
                    if next(
                        (
                            t
                            for t in synonyms
                            if t.casefold() == filter["name"].casefold()
                        ),
                        "",
                    ):
                        print(f'Synonym: update "{filter["name"]}" to "{label}"')
                else:
                    print(
                        f'Invalid label?: {filter["name"]} no longer valid for {filter["id"]} (check for additional synonym classes)'
                    )
        else:
            if old_facet != facet_name:
                print(f"skipped {facet_name}")
                pass

    for a in azul_filters:
        facet_name, azul_term = a
        for term in retriever.cached_terms[facet_name]:
            if azul_term in retriever.cached_terms[facet_name][term]["synonyms"]:
                print(
                    f'could assign azul filter "{azul_term}" to same ontology ID as "{retriever.cached_terms[facet_name][term]["label"]}"'
                )
                break

