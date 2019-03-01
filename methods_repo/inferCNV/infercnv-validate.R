#!/usr/bin/env Rscript 
# Script validate inferCNV docker container.

#####
# Data sources
#####

## input data for validation (provided in docker image)
validation_input_dir <- "/inferCNV/example"
input_gencode <- paste0(validation_input_dir, "/gencode_downsampled.txt")
input_annot <- paste0(validation_input_dir, "/oligodendroglioma_annotations_downsampled.txt")
input_matrix <- paste0(validation_input_dir, "/oligodendroglioma_expression_downsampled.counts.matrix")

## reference output for validation
#validation_reference_source <- paste0("https://raw.githubusercontent.com/",
#  "HumanCellAtlas/analysis-tools-registry-supplemental/master/",
#  "inferCNV/infercnv.png")
validation_reference_source <- paste0("https://raw.githubusercontent.com/",
  "jlchang/drafts/master/methods_repo/inferCNV/infercnv.png")
validation_reference <- paste0(validation_input_dir, "infercnv.png")

# Make sure the reference input data exists 
if (!file.exists(input_gencode) || !file.exists(input_annot) || !file.exists(input_matrix)){
    stop(paste0("Error = expected input files cannot be found."))
}

# Download reference test data for validation 
cat("***Loading test data\n")
download.file(validation_reference_source, validation_reference)


#####
# Set up environment for validation
#####

pargs <- optparse::OptionParser(usage = paste("%prog [options]",
                                            "--input file"))
args_parsed <- optparse::parse_args(pargs)
args <- args_parsed$options
args$output_dir <- "/tmp"
args$ref_groups <- list("Microglia/Macrophage", "Oligodendrocytes (non-malignant)")
args$annotations_file <- input_annot
args_parsed$args[1] <- input_matrix
args_parsed$args[2] <- input_gencode
source("/inferCNV/scripts/inferCNV.R")

#####
# Perform validation
#####

library(tools)
if md5sum("/tmp/infercnv.png") == md5sum(validation_reference) {
  cat "validation successful - infercnv.png output are the same"
} else {
  stop("validation failed - infercnv.png output differs from reference")
}
