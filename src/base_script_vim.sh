#!/bin/bash

files="$HOME/vim/src/objects/*.o"
mkdir $HOME/C_bytecode_analysis/output/vim

for file in $files;
  do
    name=${file##*/}
    check="$HOME/C_bytecode_analysis/output/vim/$name.labeled_addresses"
    if [ ! -s $check ]
    then
      eval "python3 src/main_labeler.py $file $HOME/vim/src/ /vim > log_$name.txt"
    fi
    echo -e "--\ndone ${file##*/}\n--\n";
done
