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
    outfile = input_head + '/v2.1.1_' + input_tail
    print(f'Generating new metadata file: {outfile}')

    # setting organ_region by biosample_id
    # check number of NaN in mapping column before mapping
    print(
        f"     Pre-map # of NaN for biosample_id: {sum(pd.isnull(df['biosample_id']))}"
    )
    print(
        f"biosample_id counts: {df['biosample_id'].groupby(df['biosample_id']).count()}"
    )

    # duplicate 'biosample_id' as basis for for 'organ_region' and 'organ_region__ontology_label'
    df['organ_region'] = df['biosample_id']
    df['organ_region__ontology_label'] = df['biosample_id']

    # mapping dictionary from biosample_id to array of organ_regions
    b2o = {
        "UU_D01_01": "MBA:000000909|MBA:000000502",
        "UU_D02_01": "MBA:000000909|MBA:000000502",
        "UU_D03_01": "MBA:000000909|MBA:000000502",
        "UU_D04_01": "MBA:000000909|MBA:000000502",
        "UU_D05_01": "MBA:000000909|MBA:000000502",
        "UU_D06_01": "MBA:000000909|MBA:000000502",
        "UU_D01_02": "MBA:000000714|MBA:000000972",
        "UU_D02_02": "MBA:000000714|MBA:000000972",
        "UU_D04_02": "MBA:000000714|MBA:000000972",
        "UU_D05_02": "MBA:000000714|MBA:000000972",
        "UU_D06_02": "MBA:000000985",
        "UU_D04_03": "MBA:000000302|MBA:000000294|MBA:000000795",
        "UU_D05_03": "MBA:000000302|MBA:000000294|MBA:000000795",
        "group": "group",
    }
    # mapping dictionary from biosample_id to array of organ_region__ontology_labels
    b2l = {
        "UU_D01_01": "Entorhinal area|Subiculum",
        "UU_D02_01": "Entorhinal area|Subiculum",
        "UU_D03_01": "Entorhinal area|Subiculum",
        "UU_D04_01": "Entorhinal area|Subiculum",
        "UU_D05_01": "Entorhinal area|Subiculum",
        "UU_D06_01": "Entorhinal area|Subiculum",
        "UU_D01_02": "Orbital area|Prelimbic area",
        "UU_D02_02": "Orbital area|Prelimbic area",
        "UU_D04_02": "Orbital area|Prelimbic area",
        "UU_D05_02": "Orbital area|Prelimbic area",
        "UU_D06_02": "Primary motor area",
        "UU_D04_03": "Superior colliculus, sensory related|Superior colliculus, motor related|Periaqueductal gray",
        "UU_D05_03": "Superior colliculus, sensory related|Superior colliculus, motor related|Periaqueductal gray",
        "group": "group",
    }
    df['organ_region'] = df['organ_region'].map(b2o)
    df['organ_region__ontology_label'] = df['organ_region__ontology_label'].map(b2l)
    print(
        f"     Post-map # of NaN for organ_region: {sum(pd.isnull(df['organ_region']))}"
    )
    print(
        f"organ_region counts: {df['organ_region'].groupby(df['organ_region']).count()}"
    )

    # check number of NaN in mapping column before mapping
    print(
        f"     Pre-map # of NaN for cell_type: {sum(pd.isnull(df['cell_type__ontology_label']))}"
    )
    print(
        f"cell_type__ontology_label counts: {df['cell_type__ontology_label'].groupby(df['cell_type__ontology_label']).count()}"
    )

    # duplicate 'cell_type__ontology_label' as basis for for 'cell_type__custom'
    df['cell_type__custom'] = df['cell_type__ontology_label']

    # mapping dictionary from cell_type__ontology_label to cell_type__custom
    ct2ctc = {
        "neuronal brush cell": "Unipolar brush cell (UBC)",
        "interneuron": "Molecular layer interneuron 2 (MLI2)",
        "Fibroblast": "Fibroblast",
        "cerebellar granule cell": "Granule",
        "Purkinje cell": "Molecular layer interneuron 2 (MLI2)",
        "group": "group",
    }
    df['cell_type__custom'] = df['cell_type__custom'].map(ct2ctc)
    print(
        f"     Post-map # of NaN for cell_type__custom: {sum(pd.isnull(df['cell_type__custom']))}"
    )

    print(
        f"cell_type__custom counts: {df['cell_type__custom'].groupby(df['cell_type__custom']).count()}"
    )

    tsv_file.close()

    df.to_csv(outfile, header=True, sep='\t', index=False, encoding='utf-8')
