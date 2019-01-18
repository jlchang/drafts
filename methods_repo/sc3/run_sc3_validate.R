#!/usr/bin/env Rscript

# Load libraries
suppressPackageStartupMessages(library("optparse"));
suppressPackageStartupMessages(library("SC3"));
suppressPackageStartupMessages(library("SingleCellExperiment"));
suppressPackageStartupMessages(library("logging"));

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
  download.file("https://github.com/hemberg-lab/scRNA.seq.course/raw/master/deng/deng-reads.rds",
                "deng-reads.rds")
  input_file <- "deng-reads.rds"
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
  labels_file <- "data/demo_labels.csv"
} else {
  labels_file <- "data/sc3_labels.csv"
}

#read in data
sce <- readRDS(input_file);

#run method on data
if (args_parsed$demo[1]){
    args_parsed$ks[1] <- 10
    sce <- sc3(sce, ks = args_parsed$ks[1], biology = T,
               rand_seed = args_parsed$seed[1], n_cores = 1);
} else if (args_parsed$validate[1]){
    sce <- sc3_prepare(sce, rand_seed = args_parsed$seed[1], n_cores = 1)
    sce <- sc3_calc_dists(sce)
    sce <- sc3_calc_transfs(sce)
    rounded_data <- round(metadata(sce)$sc3$transformations$pearson_laplacian,
                          digits = 8)
    transfs_result <- cbind(colnames(sce), rounded_data)
    write.table(transfs_result, file = "data/validation.csv",
                row.names = FALSE, col.names = FALSE,
                quote = FALSE, sep = ",")
    download.file("https://raw.githubusercontent.com/jlchang/drafts/master/methods_repo/sc3/reference_output.csv",
                  "data/reference_output.csv")
    if (isTRUE(all.equal(readLines("data/reference_output.csv"),
                         readLines("data/validation.csv")))) {
      logging::loginfo(paste("Successful validation - validation file matches reference"))
    } else {
      stop("validation failed")
    }
} else {
  sce <- sc3(sce, ks = args_parsed$ks[1], biology = T);
}


#save data to current working directory
saveRDS(sce, output_file)
logging::loginfo(paste("SingleCellExperiment object", output_file,
                       "saved", sep = " "))

if (args_parsed$cell_labels[1]) {
  cluster_Col <- paste0("sc3_", args_parsed$ks[1], "_clusters")
  labels <- cbind(colnames(sce), eval(parse(text = paste0("colData(sce)$",
                                                          cluster_Col))))
  write.table(labels, file = labels_file, row.names = FALSE,
              col.names = FALSE, quote = FALSE, sep = ",")
  logging::loginfo(paste("Cell labels saved in", output_file, sep = " "))
}