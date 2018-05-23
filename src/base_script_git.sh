#!/bin/bash

files1="$HOME/git/*.o"
files2="$HOME/git/*/*.o"

for file in $files2;
  do
    name=${file##*/}
    check="$HOME/C_bytecode_analysis/output/$name.labeled_addresses"
    if [ ! -s $check ]
    then
      eval "python3 src/main_labeler.py $file $HOME/git/ > log_$name.txt"
    fi
    echo -e "--\ndone ${file##*/}\n--\n";
done

for file in $files1;
  do
    name=${file##*/}
    check="$HOME/C_bytecode_analysis/output/$name.labeled_addresses"
    if [ ! -s $check ]
    then
      eval "python3 src/main_labeler.py $file $HOME/git/ > log_$name.txt"
    fi
    echo -e "--\ndone ${file##*/}\n--\n";
done
