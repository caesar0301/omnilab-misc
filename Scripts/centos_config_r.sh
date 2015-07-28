#!/bin/bash

set -e

which R > /dev/null 2>&1
if [ $? == 1 ]; then
  sudo yum install -y R
fi

sudo yum install -y libcurl-devel openssl-devel libxml2-devel libxslt-devel

sudo yum install -y gdal proj geos geos-devel gdal-devel

R -e "install.packages(setdiff(c('devtools', 'dplyr', 'tidyr', 'data.table', 'reshape', 'reshape2', 'plyr'), rownames(installed.packages())), repo='http://cran.rstudio.com')"

R -e "install.packages(setdiff(c('ggplot2', 'gplots', 'gridExtra', 'ggvis', 'plotrix', 'scatterplot3d', 'colorRamps', 'grDevices', 'RColorBrewer', 'colorspace', 'dichromat'), rownames(installed.packages())), repo='http://cran.rstudio.com')"

R -e "install.packages(setdiff(c('MASS', 'Hmisc', 'classInt', 'parallel', 'doBy', 'squash'), rownames(installed.packages())), repo='http://cran.rstudio.com')"

R -e "install.packages(setdiff(c('depmixS4', 'entropy', 'psych', 'fields'), rownames(installed.packages())), repo='http://cran.rstudio.com')"

R -e "install.packages(setdiff(c(), rownames(installed.packages())), repo='http://cran.rstudio.com')"

R -e "install.packages(setdiff(c(), rownames(installed.packages())), repo='http://cran.rstudio.com')"

R -e "install.packages(setdiff(c(), rownames(installed.packages())), repo='http://cran.rstudio.com')"


R -e "devtools::install_github('jalvesaq/colorout')"

curl https://raw.githubusercontent.com/caesar0301/omnilab-misc/master/Scripts/.Rprofile -o ~/.Rprofile

echo "Done!"
