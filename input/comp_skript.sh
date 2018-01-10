#!/bin/bash
e=".out"
for f in *.c; do gcc -g $f -o ${f::-2}$e; done
