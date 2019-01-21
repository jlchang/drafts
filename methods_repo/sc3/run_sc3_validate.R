#!/usr/bin/env Rscript

# Load libraries
suppressPackageStartupMessages(library("optparse"));
suppressPackageStartupMessages(library("logging"));
suppressPackageStartupMessages(library("here"));
suppressPackageStartupMessages(library("SC3"));
suppressPackageStartupMessages(library("SingleCellExperiment"));


# Data sources
## input data for demo and validation
demo_input_source <- "https://github.com/hemberg-lab/scRNA.seq.course/raw/master/deng/deng-reads.rds"
demo_input <- here("deng-reads.rds")
## reference output for validation
## TEMPORARY LOCATION for script development
reference_source <- "https://raw.githubusercontent.com/jlchang/drafts/master/methods_repo/sc3/reference_output.csv"
reference_output <- here("reference_output.csv")

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
            metavar = "/path/to/input/file",
            help = paste("Input file for analysis.",
                         "SingleCellExperiment object in rds file format"))

pargs <- optparse::add_option(pargs, c("--cell_labels"),
            type = "logical",
            default = FALSE,
            action = "store_true",
            dest = "cell_labels",
            help = paste("generate cell labels from clustering run,",
                         "sc3_labels.csv [Default %default]"))

pargs <- optparse::add_option(pargs, c("--demo"),
            type = "logical",
            default = FALSE,
            action = "store_true",
            dest = "demo",
            help = paste("generate cell labes for demo data, demo_labels.csv",
                         "[Default %default]"))

pargs <- optparse::add_option(pargs, c("--validate"),
            type = "logical",
            default = FALSE,
            action = "store_true",
            dest = "validate",
            help = paste("generate validation output file, validation.csv",
                         "[Default %default]"))
                         
pargs <- optparse::add_option(pargs, c("--ks"),
            type = "character",
            default = "5",
            action = "store",
            dest = "ks",
            metavar = "number or range",
            help = paste("range of number of clusters,",
                         "k, used for SC3 clustering",
                         "Can also be a single integer.",
                         "[Default %default]"))
                         
pargs <- optparse::add_option(pargs, c("--seed"),
            type = "integer",
            default = 1,
            action = "store",
            dest = "seed",
            help = paste("Set random seed to enable reproducible behavior",
                         "[Default %default]"))

pargs <- optparse::add_option(pargs, c("--stdoutfile"),
            type = "character",
            default = "stdout.txt",
            action = "store",
            dest = "stdoutfile",
            help = paste("Filename for messages captured from stdout.",
                         "[Default %default]"))
                     
                         
args_parsed <- optparse::parse_args(pargs)

if (args_parsed$demo[1] || args_parsed$validate[1]){
  download.file(demo_input_source, demo_input)
  input_file <- demo_input
} else {
  input_file <- args_parsed$input[1]
}

# Make sure the input data exists
if (!file.exists(input_file)){
    error_message <- paste0("Input file, ",
    input_file, ", does not exist. ",
    "Please check your input and try again.")
    logging::logerror(error_message)
    stop(error_message)
}

logging::loginfo(paste("Analyzing", input_file, sep = " "))

#Define output name based on input name. 
#If path to file is provided, path is maintained
base_in <- basename(input_file)
dir_in <- dirname(input_file)
if (dir_in == "." ){
output_file <- paste0("SC3-", base_in)
} else {
output_file <- paste0(dir_in, "/", "SC3-", base_in)
}

if (args_parsed$demo[1]){
  args_parsed$cell_labels[1] <- TRUE
  labels_file <- "validation.csv"
} else {
  labels_file <- "sc3_labels.csv"
}

#read in data
sce <- readRDS(input_file);

#for demo mode, run SC3 on demo data with k=10 to match on-line example
if (args_parsed$demo[1]){
    args_parsed$ks[1] <- 10
    sce <- sc3(sce, ks = args_parsed$ks[1], biology = T,
               rand_seed = args_parsed$seed[1], n_cores = 1);

#for validation, only run SC3 protocol to last deterministic step, sc3_calc_transfs
} else if (args_parsed$validate[1]){
    sce <- sc3_prepare(sce, rand_seed = args_parsed$seed[1], n_cores = 1)
    sce <- sc3_calc_dists(sce)
    sce <- sc3_calc_transfs(sce)

    #TEMPORARY home for reference output
    download.file(reference_source, reference_output)
    ref <- read.table(reference_output, header = FALSE, row.names = 1, sep = ",")
    #check calls (row names) match between reference and validation output
    if (isTRUE(all.equal(colnames(sce),rownames(ref)))) {
      logging::loginfo(paste("Cell names in validation output match reference"))
    #if cells don't match, make validation and reference files available and exit
    } else {
      transfs_result <- cbind(colnames(sce), metadata(sce)$sc3$transformations$pearson_laplacian)
      write.table(transfs_result, file = here("data", "validation.csv"),
                row.names = FALSE, col.names = FALSE,
                quote = FALSE, sep = ",")
      file.copy(reference_output, here("data", reference_output))
      stop("validation failed - cell names in validation and reference data do not match")
    }
    #coerce the reference data in preparation for calculating relative error
    test_matrix <- as.matrix(ref)

    #check whether largest relative error is larger than acceptable threshold
    if (max( abs((as.matrix(metadata(sce)$sc3$transformations$pearson_laplacian)) 
         - test_matrix) / abs(test_matrix)) < 1.0e-8) {
      logging::loginfo(paste("Successful validation - validation file matches reference"))
    #if max relative error exceeds threshold, make validation and reference files available and exit
    } else {
      transfs_result <- cbind(colnames(sce), metadata(sce)$sc3$transformations$pearson_laplacian)
      write.table(transfs_result, file = here("data", "validation.csv"),
                row.names = FALSE, col.names = FALSE,
                quote = FALSE, sep = ",")
      file.copy(reference_output, here("data", reference_output))
      stop("validation failed - max relative error in validation data exceeds threshold")
    }
} else {
  sce <- sc3(sce, ks = args_parsed$ks[1], biology = T);
  #save data to current working directory
  saveRDS(sce, output_file)
  logging::loginfo(paste("SingleCellExperiment object", here("data", here("data", output_file),
                       "saved", sep = " "))
}


if (args_parsed$cell_labels[1]) {
  cluster_Col <- paste0("sc3_", args_parsed$ks[1], "_clusters")
  labels <- cbind(colnames(sce), eval(parse(text = paste0("colData(sce)$",
                                                          cluster_Col))))
  write.table(labels, file = here("data", labels_file), row.names = FALSE,
              col.names = FALSE, quote = FALSE, sep = ",")
  logging::loginfo(paste("Cell labels saved in", output_file, sep = " "))
}
