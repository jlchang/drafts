#!/usr/bin/env Rscript

# Load libraries
suppressPackageStartupMessages(library("optparse"))
suppressPackageStartupMessages(library("logging"))
suppressPackageStartupMessages(library("slingshot"))
suppressPackageStartupMessages(library("SingleCellExperiment"))

# Set up logging
# Logging level choices
C_LEVEL_CHOICES <- names(loglevels)
#initialize to info setting.
logging::basicConfig(level = "INFO")

# Command line arguments
pargs <- optparse::OptionParser(usage = paste("%prog [options]",
                                            "--input file"))

# input (string) path to SingleCellExperiment object
pargs <- optparse::add_option(pargs, c("--input"),
            type = "character",
            action = "store",
            dest = "input",
            metavar = "Input",
            help = paste("Input file for analysis. SlingshotDataSet",
                         "matrix,SingleCellExperiment object in rds file format.",
                         "If reducedDim is a SlingshotDataSet,",
                         "cluster labels will be taken from it.",
                         "[REQUIRED]"))
                         
pargs <- optparse::add_option(pargs, c("--clusterLabels"),
            type = "character",
            default = NULL,
            action = "store",
            dest = "clusterLabels",
            metavar = "clusterLabels",
            help = paste("Vector of length n denoting cluster labels",
                         "optionally including -1’s for 'unclustered.'",
                         "[Default %default], (optional)"))
                         
pargs <- optparse::add_option(pargs, c("--start.clus"),
            type = "character",
            default = NULL,
            action = "store",
            dest = "start.clus",
            metavar = "start.clus",
            help = paste("Indicates the cluster(s) *from*",
                         "which lineages will be drawn",
                         "[Default %default], (optional)"))
                         
pargs <- optparse::add_option(pargs, c("--end.clus"),
            type = "character",
            default = NULL,
            action = "store",
            dest = "end.clus",
            metavar = "end.clus",
            help = paste("Indicates the cluster(s) which will",
                         "be forced leaf nodes in their trees",
                         "[Default %default], (optional)"))

# Check arguments to ensure user input meets certain requirements.    
check_arguments <- function(arguments){
  # Require an input file
  if (( ! ("input" %in% names(arguments) )) ||
       (arguments$input == "") ||
       (is.na(arguments$input))) {
       logging::logerror(paste(":: --input: enter a file path to ",
                               "the input data.", sep = ""))
        stop("error, no --input specified")
  }
  # Make sure the input data file exists
  if ( ! file.exists(arguments$input)){
    error_message <- paste0("Provided input file, ",
    arguments$input, ", does not exist. ",
    "Please check your input and try again")
    stop(error_message)
  }
  # Require clusterLabels if input is csv file
  # csv format implies input is matrix of reduced dimensional coordinates
  # Parse input filename
  input_file <- unlist(strsplit(args$input, "[.]"))
  arguments$input_suffix <- input_file[length(input_file)]
  if ( arguments$input_suffix == "csv") {
    if (( ! ("clusterLabels" %in% names(arguments) )) ||
       (arguments$clusterLabels == "") ||
       (is.na(arguments$clusterLabels))) {
       logging::logerror(paste(":: --clusterLabels: enter file path to",
                               "a vector of cluster labels in csv format."))
        stop(paste("error, no --clusterLabels provided, clusterLabels csv file required",
                    "if input data is matrix (csv) of reduced dimensional coordinates."))
    }
  }
  #Define output name based on input name. 
  #If path to file is provided, path is maintained
  # Set the default name of an output rds file
  arguments$output_file <- paste0(input_file[1:length(input_file) - 1],
                      "-slingshot.", input_file[length(input_file)])
  return(arguments)
}


#process user-submitted inputs and set defaults
args_parsed <- optparse::parse_args(pargs, positional_arguments = TRUE)
args <- args_parsed$options
logging::loginfo(paste("Checking input arguments", sep = "" ))
args <- check_arguments(args)

#read in data and run slingshot
if ( args$input_suffix == "rds" ) {
  sce <- readRDS(args$input)
  result <- slingshot(sce)
} else if ( args$input_suffix == "csv" ) {
    coordinates <- read.csv2(args$input)
    labels <- read.csv2(args$clusterLabels)
    result <- slingshot(coordinates,labels)
}


#save data to current working directory
saveRDS(result, args$output_file)
