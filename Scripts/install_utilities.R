# This script makes it easy to install my daily toolkit via
# one command.
#     > source("install_utilities.R")
#
# By xiaming
# chenxm35@gmail.com

install.packages(c(
    # Data wrangling
    "reshape", "reshape2", "tidyr", "plyr", "dplyr",

    # Plots and colors
    "ggplot2", "gplots", "gridExtra", "ggvis", "plotrix",
    "scatterplot3d", "colorRamps", "grDevices", "RColorBrewer",
    "colorspace", "dichromat",

    # Misc tools
    "MASS", "Hmisc", "classInt", "parallel", "doBy", "squash",

    # Models
    "depmixS4", "entropy", "psych",

    # Spatio-temporal data
    "fields", "rgdal", "raster", "spdep", "spacetime", "gstat",
    "RandomFields", "CompRandFld", "zoo", "xst", "geoR",

    # Maps
    "maptools", "mapproj", "maps", "osmar", "OpenStreetMap", "GISTools",
    "splancs", "PBSmapping", "deldir",

    # Spatial correlation
    "ade4", "ape", "ncf", "pgirmess", "spatial", "mpmcorrelogram",

    # Distribution parameter estimation
    "fitdistrplus", "mixtools", "mixdist"

), repo="http://cran.rstudio.com/")
