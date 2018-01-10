# C_bytecode_analysis
>repository for analysis of ELF files written in C programming language

## DEPENDENCIES
- [Python 3.x](https://www.python.org/) - language used
- [pyelftools](https://github.com/eliben/pyelftools) - Critical dependency used for the addr2line tool
- [pycparser](https://github.com/eliben/pycparser) - used for the c_lexer tool and is currently not needed but will become useful when we start to parse C gramatics

## Install
- to install pyelftools and pycparser simply clone the git repositories position into the respective folder and run for each:
> sudo python3 setup.py install
- this repository requires no installation simply clone it and use it

## Usage
- to use the tools run:
> python3 src/<tool_name>.py input/<file_name>
- then search for your results in the output folder
- C_lexer.py, labels.py, labels_with_lex.py take C source code as input
- pyelfaddr2line.py and label_lines.py take the ELF .out file as input
- A21.c is the test file it is in the input folder and should be compiled using:
> gcc -g A21.c -o A21.out
- the tools also work with .obj files
- comp_script is a bash script which compiles all of the C files in input

## Description
- pyelfaddr2line will construct a list of all the files a addres in the .text section was compiled from, it outputs to .addr2line file
- c_lexer.py returns the tokens used for lexical analysis, outputs to .lexed file
- labels* get the encapsulations of C source code, outputs to .labels file (this has been replaced with the labels_with_lex.py tool which works faster and better, but still has the same input output)
- label_lines uses the all the other programs to label addresses in the ELF file, outputs to .labeled_addresses file

