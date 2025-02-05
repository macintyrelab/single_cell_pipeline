
suppressMessages(library(QDNAseqmod))
suppressWarnings(library(argparse))
suppressWarnings(library(this.path))
options(future.globals.maxSize=850*1024^2)

## ARGUMENTS
parser <- argparse::ArgumentParser(description='Run pipeline for plotting relative copy number profiles')
parser$add_argument('--bin.size', type = "integer", required = TRUE,
                    help = "bin size in kilobase. To quantify CNSigs, the bin size must be '30'")
parser$add_argument('--out.dir', type = "character", required = TRUE,
                    help = "name of the directory where the output files will be placed. The pipeline will create the ouput directory")

args <- parser$parse_args()

OUTDIR <- args$out.dir
bin.size <- args$bin.size

readCounts <- readRDS(paste0(OUTDIR,"/readCounts_",bin.size,"kb.rds"))
readCountsFiltered <- readRDS(paste0(OUTDIR,"/readCountsFiltered_",bin.size,"kb.rds"))
copyNumbersSegmented <- readRDS(paste0(OUTDIR,"/copyNumbersSegmented_",bin.size,"kb.rds"))

## PLOTING RESULTS
samples <- readCounts@phenoData@data$name

# noisePlot: plot showing the relationship between the observed standard deviation in the data and its read depth
png(paste0(OUTDIR, "/noisePlot.png"), width = 180, height = 180, units = "mm", res = 300)
tryCatch(
 print(noisePlot(readCountsFiltered)),
  error = function(e) {
    message("Error while trying to generate noisePlot.png :")
    message(e)
  },
  finally = dev.off()
)

# isobarPlot: plot showing the median read counts as a function of GC content and mappability
for (s in samples){
  png(paste0(OUTDIR,"/",s,"_isobarPlots.png"), width = 180, height = 180, units = "mm", res = 300)
  tryCatch(
    print(isobarPlot(readCountsFiltered[,s])),
    error = function(e) {
      message(paste0("Error while trying to generate ", OUTDIR,"/",s,"_isobarPlots.png :"))
      message(e)
    },
    finally = dev.off()
  )
}

# relativeCN: plot with the relative copy numbers
for (s in samples){
  png(paste0(OUTDIR,"/", s, "_relativeCN.png"), width = 180, height = 180, units = "mm", res = 300)
  tryCatch(
  {
    ymax=as.numeric(round(3*mean(copyNumbersSegmented@assayData$copynumber[,s], na.rm=T)))
    plot(copyNumbersSegmented[,s], logTransform=F, ylim=c(0,ymax))},
    error = function(e) {
      message(paste0("Error while trying to generate ", OUTDIR,"/", s, "_relativeCN.png :"))
      message(e)
    },
    finally = dev.off())
}
