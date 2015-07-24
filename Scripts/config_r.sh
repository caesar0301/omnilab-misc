#!/bin/bash

set -e

which R > /dev/null 2>&1
if [ $? == 1 ]; then
  sudo yum install -y R
fi

R -e "install.packages(c('dplyr', 'tidyr', 'ggplot2', 'data.table'), repo='http://cran.rstudio.com')"

R -e "devtools::install_github('jalvesaq/colorout')"

curl https://github.com/caesar0301/omnilab-misc/raw/master/Scripts/.Rprofile -o ~/.Rprofile

echo "Done!"
