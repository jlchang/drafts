#!/usr/bin/env Rscript

# Load libraries
suppressPackageStartupMessages(library("optparse"));
suppressPackageStartupMessages(library("SC3"));
suppressPackageStartupMessages(library("SingleCellExperiment"));

# Command line arguments
pargs <- optparse::OptionParser(usage = paste("%prog [options]",
                                            "--input file"))

# input (string) path to SingleCellExperiment object
pargs <- optparse::add_option(pargs, c("--input"),
            type = "character",
            action = "store",
            dest = "input",
            metavar = "Input",
            help = paste("Input file for analysis.",
                         "SingleCellExperiment object in rds file format",
                         "[REQUIRED]"))
                         
pargs <- optparse::add_option(pargs, c("--ks"),
            type = "character",
            default = "5",
            action = "store",
            dest = "ks",
            metavar = "ks",
            help = paste("range of number of clusters, ",
                         "k, used for SC3 clustering",
                         "Can also be a single integer.",
                         "[Default %default]"))
                     
# Check arguments to ensure user input meets certain requirements.    
check_arguments <- function(arguments){
    if ( (!( "input" %in% names(arguments))) ||
         (arguments$input == "") ||
         (is.na(arguments$input)) ) {
      stop("error, no --input")
    }
  return(arguments)
}
                         
args_parsed <- optparse::parse_args(pargs)

args_parsed <- check_arguments(args_parsed)


# Make sure the input data exists
if (!file.exists(args_parsed$input[1])){
    error_message <- paste0("Input file, ",
    args_parsed$input[1], ", does not exist. ",
    "Please check your input and try again.")
    stop(error_message)
}

#Define output name based on input name. 
#If path to file is provided, path is maintained
input_file <- unlist(strsplit(args_parsed$input[1], "[.]"))
output_file <- paste0(input_file[1:length(input_file) - 1],
                      "-SC3.", input_file[length(input_file)])

#read in data
sce <- readRDS(args_parsed$input[1]);

#run method on data
sce <- sc3(sce, ks = args_parsed$ks[1], biology = T);

#generate data

#save data to current working directory
saveRDS(sce, output_file)
