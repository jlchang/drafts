"""Python script template

DESCRIPTION
Template to take in a command line argument for a file

EXAMPLE
python python_template.py <file>
"""

import argparse
import csv


def create_parser():
    """Parse command line values
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('input', help='input TSV file')
    return parser


if __name__ == '__main__':
    args = create_parser().parse_args()
    arguments = vars(args)

    tsv_file = open(args.input, 'r')
    read_tsv = csv.reader(tsv_file, delimiter="\t")
    for row in read_tsv:
        print(row)
    tsv_file.close()
