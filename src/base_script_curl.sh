#!/bin/bash

files="$HOME/curl/src/*.o"
mkdir $HOME/C_bytecode_analysis/output/curl

for file in $files;
  do
    name=${file##*/}
    check="$HOME/C_bytecode_analysis/output/curl/$name.labeled_addresses"
    if [ ! -s $check ]
    then
      eval "python3 src/main_labeler.py $file $HOME/curl/ /curl > log_$name.txt"
    fi
    echo -e "--\ndone ${file##*/}\n--\n";
done
