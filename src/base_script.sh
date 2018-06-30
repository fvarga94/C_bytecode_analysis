#!/bin/bash

dir="$1"
oflag="_$2"

files=$(find $HOME/$dir/ -name '*.o')

if [ ! -d $HOME/C_bytecode_analysis/output/$dir$oflag ]
then
  mkdir $HOME/C_bytecode_analysis/output/$dir$oflag
fi

for file in $files;
  do
    name=${file##*/}
    check="$HOME/C_bytecode_analysis/output/$dir$oflag/$name.labeled_addresses"
    if [ ! -s $check ]
    then
      eval "python3 src/main_labeler.py $file $HOME/$dir/ /$dir$oflag > log/log_$name.txt"
    fi
    echo -e "--\ndone ${file##*/}\n--\n";
done
echo "complete" > $HOME/C_bytecode_analysis/output/$dir$oflag/complete.txt
