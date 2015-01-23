#!/bin/bash
# By Xiaming Chen
set -e
sudo -s

EXEC="create-lvm"

curl -L https://github.com/caesar0301/omnilab-misc/raw/master/Scripts/auto-create-lvm.sh \
     > /usr/local/bin/$EXEC

chmod +x /usr/local/bin/$EXEC
