#!/bin/bash
# Run mark_session_ip.py in a batch mode.
# By chenxm
# chen_xm@sjtu.edu.cn

if [ $# -lt 2 ]; then
	echo "Usage: $0 <raw-session-folder> <output-folder>" && exit 1;
fi

input=$1
output=$2

if [ -e $output ]; then
	echo "$output exists already. Please select another." && exit 1;
fi

mkdir -p $output

for filename in `ls $input`; do
	filename=$input/$filename
	echo "Parsing $filename .. "
	`dirname $0`/mark_session_ip.py $filename $output/`basename $filename`
done