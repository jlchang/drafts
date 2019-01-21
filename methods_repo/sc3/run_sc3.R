#!/usr/bin/env Rscript

# Load libraries
suppressPackageStartupMessages(library("optparse"));
suppressPackageStartupMessages(library("logging"));
suppressPackageStartupMessages(library("here"));
suppressPackageStartupMessages(library("SC3"));
suppressPackageStartupMessages(library("SingleCellExperiment"));


# Data sources

## input data for demo and validation
demo_input_source <- paste0("https://github.com/hemberg-lab/",
  "scRNA.seq.course/raw/master/deng/deng-reads.rds")
demo_input_h <- here("deng-reads.rds")

## reference output for validation
## TEMPORARY LOCATION for script development
reference_source <- paste0("https://raw.githubusercontent.com/",
  "jlchang/drafts/master/methods_repo/sc3/reference_output.csv")
reference_output_h <- here("reference_output.csv")

## TEMPORARY "bad" reference output script development
bad_cell_source <- paste0("https://raw.githubusercontent.com/",
  "jlchang/drafts/master/methods_repo/sc3/bad_cell.csv")
bad_value_source <- paste0("https://raw.githubusercontent.com/",
  "jlchang/drafts/master/methods_repo/sc3/bad_value.csv")



# Set up logging
# Logging level choices
C_LEVEL_CHOICES <- names(loglevels)
#initialize to info setting.
logging::basicConfig(level = "INFO")

# Command line arguments
pargs <- optparse::OptionParser(usage = paste("%prog [options]"))

pargs <- optparse::add_option(pargs, c("--input"),
            type = "character",
            action = "store",
            dest = "input",
            metavar = "<path to input file>",
            help = paste("Input file for analysis.",
                         "SingleCellExperiment object in rds file format"))

pargs <- optparse::add_option(pargs, c("--cell_labels"),
            type = "logical",
            default = FALSE,
            action = "store_true",
            dest = "cell_labels",
            help = paste("generate cell labels from clustering run,",
                         "SC3_labels.csv [Default %default]"))

                         
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
            default = "SC3_log.txt",
            action = "store",
            dest = "stdoutfile",
            help = paste("Filename for messages captured from stdout.",
                         "[Default %default]"))


pargs <- optparse::add_option(pargs, c("--demo"),
                              type = "logical",
                              default = FALSE,
                              action = "store_true",
                              dest = "demo",
                              help = paste("run SC3 demo",
                                      "[Default %default]"))

pargs <- optparse::add_option(pargs, c("--validate"),
                              type = "logical",
                              default = FALSE,
                              action = "store_true",
                              dest = "validate",
                              help = paste("run SC3 validation,",
                                          "[Default %default]"))

## TEMPORARY options script development 
## (accepted options: "reference", "bad_cell", "bad_value")
pargs <- optparse::add_option(pargs, c("--validation_type"),
                              type = "character",
                              default = "reference",
                              action = "store",
                              metavar = "",
                              dest = "val_type")
                     
                         
args_parsed <- optparse::parse_args(pargs)

# set logging to capture stdout to log file
addHandler(writeToFile, file = here(args_parsed$stdoutfile[1]))

#download test data set if running validation or demo
if (args_parsed$demo[1] || args_parsed$validate[1]) {
  download.file(demo_input_source, demo_input_h)
  input_file_h <- demo_input_h
} else {
  input_file_h <- here(args_parsed$input[1])
}

# Make sure the input data exists
if (!file.exists(input_file_h)){
    error_message <- paste0("Input file, ",
    input_file_h, ", does not exist. ",
    "Please check your input and try again.")
    logging::logerror(error_message)
    stop(error_message)
}

logging::loginfo(paste("Analyzing", input_file_h, sep = " "))

#Define output name based on input name. 
#If path to file is provided, maintain path for rds and labels files
## define rds output file name
base_in <- basename(input_file_h)
dir_in <- dirname(input_file_h)
output_file_h <- paste0(dir_in, "/", "SC3-", base_in)
## define cell labels file name
if (args_parsed$demo[1]){
  args_parsed$cell_labels[1] <- TRUE
  labels_file_h <- here("demo_labels.csv")
} else {
  if (! dir_in == "." ) {
    labels_file_h <- paste0(dir_in, "/", "SC3_labels.csv")
  } else {
    labels_file_h <- here("SC3_labels.csv")
  }
}

#read in data
sce <- readRDS(input_file_h)

#for demo mode, run SC3 on demo data with k=10 to match on-line example
if (args_parsed$demo[1]) {
    args_parsed$ks[1] <- 10
    sce <- sc3(sce, ks = args_parsed$ks[1], biology = T,
               rand_seed = args_parsed$seed[1], n_cores = 1)
    #clean up downloaded test data
    file.remove(input_file_h)
#if validating, stop at last deterministic step (sc3_calc_transfs)
} else if (args_parsed$validate[1]) {
    sce <- sc3_prepare(sce, rand_seed = args_parsed$seed[1], n_cores = 1)
    sce <- sc3_calc_dists(sce)
    sce <- sc3_calc_transfs(sce)

    #clean up downloaded test data before running validation steps
    file.remove(input_file_h)

    ## TEMPORARY option parsing script development
    if (args_parsed$val_type[1] == "reference") {
      download.file(reference_source, reference_output_h)
    } else if (args_parsed$val_type[1] == "bad_cell") {
      download.file(bad_cell_source, reference_output_h)
    } else if (args_parsed$val_type[1] == "bad_value") {
      download.file(bad_value_source, reference_output_h)
    } else {
      stop("bad value for validation_type parameter")
    }

    #check if reference file exists
    if (!file.exists(reference_output_h)){
      error_message <- paste0("Reference file, ",
                              reference_output_h, ", does not exist. ",
                              "Please try again.")
      logging::logerror(error_message)
      stop(error_message)
    }

    #check calls (row names) match between reference and validation output
    ref <- read.table(reference_output_h, header = FALSE,
                      row.names = 1, sep = ",")
    if (isTRUE(all.equal(colnames(sce), rownames(ref)))) {
      logging::loginfo(paste("Cell names in validation output match reference"))
    #if cell name mis-match, make validation & reference file available and exit
    } else {
      transfs_result <- cbind(colnames(sce),
                        metadata(sce)$sc3$transformations$pearson_laplacian)
      write.table(transfs_result, file = here("validation.csv"),
                row.names = FALSE, col.names = FALSE,
                quote = FALSE, sep = ",")
      ref_name <- paste0(args_parsed$val_type[1], ".csv")
      file.rename(reference_output_h, here(ref_name))
      cell_check_fail <- paste("validation failed",
                          "- cell names do not match reference")
      logging::logerror(cell_check_fail)
      stop(cell_check_fail)
    }
    #coerce the reference data in preparation for calculating relative error
    test_matrix <- as.matrix(ref)

    #check whether largest relative error is larger than acceptable threshold
    if (max ( abs(as.matrix(metadata(sce)$sc3$transformations$pearson_laplacian)
         - test_matrix) / abs(test_matrix)) < 1.0e-8) {
      file.remove(reference_output_h)
      logging::loginfo(paste("Successful validation -",
                            "validation file matches reference"))
    #if max relative error exceeds threshold,
    #make validation and reference files available and exit
    } else {
      transfs_result <- cbind(colnames(sce),
                          metadata(sce)$sc3$transformations$pearson_laplacian)
      write.table(transfs_result, file = here("validation.csv"),
                  row.names = FALSE, col.names = FALSE,
                  quote = FALSE, sep = ",")
      ref_name <- paste0(args_parsed$val_type[1], ".csv")
      file.rename(reference_output_h, here(ref_name))
      cell_value_fail <- paste("validation failed",
                               "- max relative error exceeds threshold")
      logging::logerror(cell_value_fail)
      stop(cell_value_fail)
    }
# run full sc3 analysis on user-supplied input data
} else {
  sce <- sc3(sce, ks = args_parsed$ks[1], biology = T);
}

#save data to current working directory
saveRDS(sce, output_file_h)
logging::loginfo(paste("SingleCellExperiment object", output_file_h,
                       "saved", sep = " "))

#if requested, save cell labels file
if (args_parsed$cell_labels[1]) {
  cluster_Col <- paste0("sc3_", args_parsed$ks[1], "_clusters")
  labels <- cbind(colnames(sce), eval(parse(text = paste0("colData(sce)$",
                                                          cluster_Col))))
  write.table(labels, file = labels_file_h, row.names = FALSE,
              col.names = FALSE, quote = FALSE, sep = ",")
  logging::loginfo(paste("Cell labels saved in", labels_file_h, sep = " "))
}
