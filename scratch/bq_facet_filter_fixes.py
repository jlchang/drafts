"""Python script template

PREREQ - before running script
    source ~/bin/setup_mongo_prod

DESCRIPTION
Template to take in a command line argument to open a TSV file in pandas dataframe

EXAMPLE
python bq_facet_filter_fixes.py <input file>

Input file is relevant sections of this Mongoid query of the SCP production database:
facets = SearchFacet.where(is_ontology_based: true)
facets.each do |f|
  p f.name
  p f.ontology_urls
  p f.filters_with_external
end

"""

import argparse
import os
from pymongo import MongoClient
import pprint
from validate_metadata import (
    OntologyRetriever,
    MAX_HTTP_REQUEST_TIME,
    MAX_HTTP_ATTEMPTS,
)


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

    if os.environ.get("DATABASE_HOST") is not None:
        host = os.environ["DATABASE_HOST"]
        user = os.environ["MONGODB_USERNAME"]
        password = os.environ["MONGODB_PASSWORD"]
        db_name = os.environ["DATABASE_NAME"]

        try:
            client = MongoClient(
                host,
                username=user,
                password=password,
                authSource=db_name,
                authMechanism="SCRAM-SHA-1",
            )

            client.server_info()
            retriever = OntologyRetriever()
            db = client[db_name]
            convention = "/Users/jlchang/Documents/GitHub/scp-ingest-pipeline/schema/alexandria_convention/alexandria_convention_schema.json"
            facets = list(db["search_facets"].find({"is_ontology_based": True}))
            for facet in facets:
                if facet["name"] == "library preparation protocol":
                    print(facet["name"])
                    print(facet["ontology_urls"])
                    for filter in facet["filters_with_external"]:
                        if filter["id"] == filter["name"]:
                            print(f'skipping Azul string {filter["id"]}')
                        else:
                            print(f'check EBI OLS for {filter["id"]}')
                            label_and_synonyms = retriever.retrieve_ontology_term_label_and_synonyms(
                                filter["id"], facet["name"], convention, "ontology"
                            )
                            label = label_and_synonyms.get("label")
                            synonyms = labels.get("synonyms")
                            if filter["name"] == label:
                                print(f'No change: {filter["name"]} is label')
                            elif filter["name"].casefold() == label.casefold():
                                print(f'CASE update: {filter["name"]} -> {label}')
                            elif synonyms:
                                if next(
                                    (
                                        t
                                        for t in synonyms
                                        if t.casefold() == provided_label.casefold()
                                    ),
                                    "",
                                ):
                                    print(
                                        f'Synonym: {filter["name"]} is synonym of {label}'
                                    )

                else:
                    print(f"skipped {facet['name']}")
                    pass
        except Exception as e:
            print(e)

    else:
        print("No DATABASE_HOST defined, did you source ~/bin/setup_mongo_prod?")

