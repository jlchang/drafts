########
## Operating System
########

### OS version 
FROM ubuntu:xenial 
MAINTAINER Martin Hemberg, mh26@sanger.ac.uk

######################
## Environment
######################

## Constants - declaring environment variables for use within the Docker container
ENV R_VERSION 3.5.1-1xenial

### locations
ENV BIN /usr/local/bin
ENV R_DATA /usr/local/R/data
ENV R_STUDIO /usr/local/R
ENV SRC /usr/local/src

######################
## Dependencies and Tools
######################

##############
## Helper tools
RUN apt-get update && \
    apt-get install -y unzip wget git

##############
## System tools
#### Enumerate operating-system level dependencies below and install using pkg management
RUN apt-get install -y --allow-unauthenticated libssl-dev libcurl4-openssl-dev libxml2-dev libxt-dev \
    libglu1-mesa-dev libfreetype6-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


##############
## Install R
RUN echo "deb http://cran.rstudio.com/bin/linux/ubuntu xenial-cran35/" | \
   tee -a /etc/apt/sources.list && \
   apt-get update && \ 
   apt-get install -y --allow-unauthenticated r-recommended=${R_VERSION} && \
   apt-get install -y --allow-unauthenticated r-base=${R_VERSION} && \
   apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN Rscript -e 'install.packages(c("optparse", "logging", "here"), repos = "http://cran.us.r-project.org")'

##############
## BiocLite for installing bioconductor packages
RUN echo "source(\"https://bioconductor.org/biocLite.R\")" > ${SRC}/install_pkgs.R && \
echo "biocLite(\"SC3\", dependencies=TRUE)" >> ${SRC}/install_pkgs.R && \
Rscript ${SRC}/install_pkgs.R
    
##############
## Install wrapper script
CMD ["/bin/mkdir", "/software/scripts", "/software/inputs"]
###TEMPORARY location of script file
ADD https://github.com/jlchang/drafts/raw/master/methods_repo/sc3/run_sc3.R /software/scripts/run_sc3.R
