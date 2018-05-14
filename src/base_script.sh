#!/bin/bash

files="$HOME/vim/src/objects/*.o"
ls -R | awk ':$/&&f{s=$0;f=0}:$/&&!f{sub(/:$/,"");s=$0;f=1;next} NF&&f{ print s"/"$0 }'

for file in $files;
  do
    name=${file##*/}
    check="$HOME/C_bytecode_analysis/output/$name.labeled_addresses"
    if [ ! -s $check ]
    then
      eval "python3 src/main_labeler.py $file $HOME/vim/src/ > log_$name.txt"
    fi
    echo -e "--\ndone ${file##*/}\n--\n";
done
