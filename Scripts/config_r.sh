#!/bin/bash

set -e

which R > /dev/null 2>&1
if [ $? == 1 ]; then
  sudo yum install -y R
fi

sudo yum install -y libcurl-devel openssl-devel libxml2-devel libxslt-devel

R -e "install.packages(c('devtools', 'dplyr', 'tidyr', 'ggplot2', 'data.table'), repo='http://cran.rstudio.com')"

R -e "devtools::install_github('jalvesaq/colorout')"

curl https://raw.githubusercontent.com/caesar0301/omnilab-misc/master/Scripts/.Rprofile -o ~/.Rprofile

echo "Done!"
