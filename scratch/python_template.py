"""Python script template

DESCRIPTION
Template to take in a command line argument to open a TSV file in pandas dataframe

EXAMPLE
python python_template.py <file>
"""

import argparse
import pandas as pd


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
    df = pd.read_csv(tsv_file)
    print(df)
    tsv_file.close()
