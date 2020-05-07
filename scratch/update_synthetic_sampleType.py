"""Update synthetic metadata files

DESCRIPTION
Take metadata file, apply mapping and generate updated file

EXAMPLE
python update_synthetic.py <file>
"""

import argparse
import pandas as pd
import os


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
    df = pd.read_csv(tsv_file, sep='\t')

    input_head, input_tail = os.path.split(args.input)
    outfile = input_head + '/new_' + input_tail
    print(f'Generating new metadata file: {outfile}')

    # check number of NaN in mapping column before mapping
    print(f"     Pre-map # of NaN for sample_type: {sum(pd.isnull(df['sample_type']))}")
    print(f"sample_type counts: {df['sample_type'].groupby(df['sample_type']).count()}")

    # duplicate 'sample_type' as basis for for 'preservation_method'
    df['preservation_method'] = df['sample_type']

    # mapping dictionary from sample_type to biosample_type
    s2b = {
        "group": "group",
        "cell line": "CellLine",
        "organoid": "DerivedType_Organoid",
        "direct from donor - fresh": "PrimaryBioSample",
        "direct from donor - frozen": "PrimaryBioSample",
        "cultured primary cells": "PrimaryBioSample_PrimaryCulture",
    }
    df['sample_type'] = df['sample_type'].map(s2b)
    df = df.rename(columns={'sample_type': 'biosample_type'})
    print(
        f"     Post-map # of NaN for biosample_type: {sum(pd.isnull(df['biosample_type']))}"
    )
    print(
        f"biosample_type counts: {df['biosample_type'].groupby(df['biosample_type']).count()}"
    )
    # mapping dictionary from sample_type to preservation_method
    s2p = {
        "group": "group",
        "direct from donor - fresh": "Fresh",
        "direct from donor - frozen": "Frozen",
    }
    df['preservation_method'] = df['preservation_method'].map(s2p)
    print(
        f"     Post-map # of NaN for preservation_method: {sum(pd.isnull(df['preservation_method']))}"
    )

    print(
        f"preservation_method counts: {df['preservation_method'].groupby(df['preservation_method']).count()}"
    )

    # check number of NaN in mapped column after mapping
    # if preservation method column is entirely empty, remove it
    tsv_file.close()
    if df['preservation_method'][1:].isnull().all():
        del df['preservation_method']
        print('deleted empty preservation_method metadata column')
    df.to_csv(outfile, header=True, sep='\t', index=False, encoding='utf-8')
