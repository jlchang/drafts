### Single-cell consensus clustering (SC3)  | [Martin Hemberg](mailto:mh26@sanger.ac.uk)

SC3 is an unsupervised clustering method for scRNA-seq data. SC3 also estimates the number of clusters and it provides features to aid the biological interpretation of the clusters

Code Repository URL: https://github.com/hemberg-lab/SC3

Upstream registry URL: http://bioconductor.org/packages/SC3

Test data set: [deng-reads.rds](https://github.com/hemberg-lab/scRNA.seq.course/blob/master/deng/deng-reads.rds?raw=true)

Docker image:

Helper script: [run_sc3.R[(https://github.com/jlchang/drafts/blob/master/methods_repo/run_sc3_test.R)

Example command line:
```
docker run -v `pwd`:/data -w /data <docker image> Rscript run_sc3.R
```