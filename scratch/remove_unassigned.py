"""remove unassigned
DESCRIPTION
remove cells from spatial file not found in metadata file

EXAMPLE
python remove_unassigned.py <metadata> <spatial>
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

    parser.add_argument('metadata', help='metadata file')
    parser.add_argument('spatial', help='spatial file')
    return parser


if __name__ == '__main__':
    args = create_parser().parse_args()
    arguments = vars(args)

    cleaned_spatial_name = "cleaned_" + args.spatial
    if os.path.exists(cleaned_spatial_name):
            print(f"{cleaned_spatial_name} already exists, please delete file and try again")
            exit(1)
    metadata_file = open(args.metadata, 'r')
    wanted_col = [0]
    df = pd.read_csv(metadata_file, usecols=wanted_col)
    assigned = df.NAME.to_list()
    #print(assigned)
    metadata_file.close()

    spatial_file = open(args.spatial, 'r')
    cleaned_spatial = open(cleaned_spatial_name , 'a')
    spatial_index = 0
    cleaned_count = 0
    for line in spatial_file:
        if spatial_index < 2:
            cleaned_spatial.write(line)
        if line.split()[0] in assigned:
            cleaned_spatial.write(line)
            cleaned_count += 1
        spatial_index += 1
    spatial_file.close()
    cleaned_spatial.close()
    print(f"For {args.metadata}, {spatial_index - 2} lines assessed, {cleaned_count} lines retained")


