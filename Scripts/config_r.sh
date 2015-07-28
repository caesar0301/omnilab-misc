#!/bin/bash

set -e

which R > /dev/null 2>&1
if [ $? == 1 ]; then
  sudo yum install -y R
fi

sudo yum install -y libcurl-devel openssl-devel libxml2-devel libxslt-devel

R -e "install.packages(c('devtools', 'dplyr', 'tidyr', 'data.table', 'reshape', 'reshape2', 'plyr', 'ggplot2', 'gplots', 'gridExtra', 'ggvis', 'plotrix', 'scatterplot3d', 'colorRamps', 'grDevices', 'RColorBrewer', 'colorspace', 'dichromat', 'MASS', 'Hmisc', 'classInt', 'parallel', 'doBy', 'squash', 'depmixS4', 'entropy', 'psych', 'fields', 'rgdal', 'raster', 'spdep', 'spacetime', 'gstat', 'RandomFields', 'CompRandFld', 'zoo', 'xst', 'geoR', 'maptools', 'mapproj', 'maps', 'osmar', 'OpenStreetMap', 'GISTools', 'splancs', 'PBSmapping', 'deldir', 'ade4', 'ape', 'ncf', 'pgirmess', 'spatial', 'mpmcorrelogram', 'fitdistrplus', 'mixtools', 'mixdist'), repo='http://cran.rstudio.com')"

R -e "devtools::install_github('jalvesaq/colorout')"

curl https://raw.githubusercontent.com/caesar0301/omnilab-misc/master/Scripts/.Rprofile -o ~/.Rprofile

echo "Done!"
