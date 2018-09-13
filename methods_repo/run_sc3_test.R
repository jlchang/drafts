#!/usr/bin/env Rscript

# Load libraries
suppressPackageStartupMessages(library('optparse''));
suppressPackageStartupMessages(library('SC3'));
suppressPackageStartupMessages(library('SingleCellExperiment'));

# Command line arguments
pargs <- optparse::OptionParser(usage = paste("%prog [options]",
                                            "--input file"))

# input (string) path to SingleCellExperiment object
pargs <- optparse::add_option(pargs, c("--input"),
            type = "character",
            default = "deng-reads.rds",
            action = "store",
            dest = "input",
            metavar = "Input",
            help = paste("Input file for analysis.",
                         "Expect SingleCellExperiment object in rds file format",
                         "[Default %default][REQUIRED]"))
                         
pargs <- optparse::add_option(pargs, c("--ks"),
            type = "character",
            default = "5",
            action = "store",
            dest = "ks",
            metavar = "ks",
            help = paste("a range of the number of clusters k used for SC3 clustering",
                         "Can also be a single integer.", "[Default %default]"))
                         
args_parsed <- optparse::parse_args(pargs)


# Make sure the input data exists
if (!file.exists(args_parsed$input[1])){
    error_message <- paste0("Input file, ",
    args_parsed$input[1], ", does not exist. ",
    "Please check your input and try again.")
    stop(error_message)
}

input_file <- unlist(strsplit(args_parsed$input[1], "[.]"))
output_file <- paste0(input_file[1:length(input_file)-1],"-SC3.",input_file[length(input_file)])

#log ks used?
sce <- readRDS(args_parsed$input[1]);
sce <- sc3(sce, ks=args_parsed$ks[1], biology=T);
saveRDS(sce, output_file)
