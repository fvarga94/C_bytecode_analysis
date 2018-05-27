#!/bin/bash

dir="$1"

files=$(find $HOME/$dir/ -name '*.o')

if [ ! -d $HOME/C_bytecode_analysis/output/$dir ]
then
  mkdir $HOME/C_bytecode_analysis/output/$dir
fi

for file in $files;
  do
    name=${file##*/}
    check="$HOME/C_bytecode_analysis/output/$dir/$name.labeled_addresses"
    if [ ! -s $check ]
    then
      eval "python3 src/main_labeler.py $file $HOME/$dir/src/ /$dir > log_$name.txt"
    fi
    echo -e "--\ndone ${file##*/}\n--\n";
done
