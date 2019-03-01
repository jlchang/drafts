#!/usr/bin/env bash


# Script to validate inferCNV docker container.

#####
# Data sources
#####

## input data for validation (provided in docker image)
validation_input_dir="/inferCNV/example"
input_gencode="${validation_input_dir}/gencode_downsampled.txt"
input_annot="${validation_input_dir}/oligodendroglioma_annotations_downsampled.txt"
input_matrix="${validation_input_dir}/oligodendroglioma_expression_downsampled.counts.matrix"

# Make sure the reference input data exists 
if [ ! -f $input_gencode ] || [ ! -f $input_annot ] || [ ! -f $input_matrix ]; then
  { echo "Error - expected input files not found."; exit 1; }
fi


# Download reference test data for validation 
echo "***Sourcing reference output file\n"
curl -L -o  ${validation_input_dir}/infercnv.png https://raw.githubusercontent.com/jlchang/drafts/master/methods_repo/inferCNV/infercnv.png

#####
# Run inferCNV
#####

/inferCNV/scripts/inferCNV.R --output_dir=/tmp --ref_groups="Microglia/Macrophage","Oligodendrocytes (non-malignant)" \
  --annotations_file=$input_annot $input_matrix $input_gencode

#####
# Perform validation
#####

diff /tmp/infercnv.png /inferCNV/example/infercnv.png
retVal=$?
if [ $retVal -ne 0 ]; then
    echo "Validation failed - infercnv.png does not match reference output file"
    exit $retVal
fi

echo "Validation succeeded - infercnv.png matches reference output file"