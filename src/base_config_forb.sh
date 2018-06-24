#!/bin/bash

commands=$(cat $1)
dir=$2
mc="make clean"
mcd="make distclean"
bc="./src/base_script.sh git "
options=("" " -O0" " -O1" " -O2" " -O3")
index=("0" "1" "2" "3" "4")
make="make"
cfl=" CFLAGS=\"-g"

for opt in ${index[*]};
  do
    if [ -s $HOME/C_bytecode_analysis/output/$dir$oflag/complete.txt ]
    then
      continue
    fi
    eval "cd $HOME/$dir"
    eval $mc
    eval $mcd
    for command in $commands;
      do
        eval "$command$cfl${options[$opt]}\""
      done
    eval "$make"
    eval "cd $HOME/C_bytecode_analysis/"
    eval "./src/base_script.sh $dir $opt"
  done
