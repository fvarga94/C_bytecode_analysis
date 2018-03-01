#!/usr/bin/env python3
import re
import sys
import copy
from c_lexer import LEX

k_words = [ "IF","ELSE","WHILE",
            "FOR","SWITCH","DO"
            ]

def check_parenthesis(token):
    #check if token is parenthesis
    if token[1] == "LPAREN":
        return 1
    elif token[1] == "RPAREN":
        return -1
    return 0

def check_brace(token):
    #check if token is brace
    if token[1] == "LBRACE":
        return 1
elif token[1] == "RBRACE":
        return -1
    return 0

def lex_and_label(fname, src=""):
    lexer = LEX()
    tokens = lexer.lex(src+fname)
    labels = []
    do_check = 0 #flag for checking od do_while scope
    for i in range(len(tokens)):
        if tokens[i][1] in k_words:
            #SOLVE capsules
            if tokens[i][1] == "DO":
                do_check = 1
            if tokens[i][1] == "WHILE" and do_check == 1:
                do_check = 0 #if finished solving of do_while scope skip next while command
                continue
            is_encapsulating = 0
            paren = 0
            start = i+1
            if tokens[i+1][1] == "LBRACE":
                #if starts new scope with {}
                is_encapsulating = 1
            else:
                #else it only encapsulates one command directly
                #eg. for (int i=0;i<5;i++) t++;
                for j in range(i + 1, len(tokens)):
                    #skip the condition part
                    paren += check_parenthesis(tokens[j])
                    #if the form is token (<condition>) {
                    #then encapsulation is starting
                    if tokens[j][1] == "RPAREN" and paren == 0:
                        if tokens[j + 1][1] == "LBRACE":
                            is_encapsulating = 1
                            start = j + 1
                            break
                        else:
                            break
            if is_encapsulating == 1:
                brace = 0
                end = 0
                #find the end of encapsulation
                for j in range(start, len(tokens)):
                    brace += check_brace(tokens[j])
                    if tokens[j][1] == "RBRACE" and brace == 0:
                        end = j
                        break
                labels.append((tokens[i][2], tokens[i][1], tokens[end][2], i)) #start event
                labels.append((tokens[end][2], tokens[i][1], i)) #end event
            else:
                #solves eg. for (int i=0; i<5; i++) for (int j=0; j<5; j++) {t++;}
                end = 0
                paren = 0
                brace = 0
                brace_check = 0
                for j in range(start, len(tokens)):
                    if tokens[j][1] == "LBRACE":
                        if brace_check == 0 and brace == 0:
                            brace_check = 1
                    brace += check_brace(tokens[j])
                    paren += check_parenthesis(tokens[j])
                    if brace == 0 and paren == 0:
                        if brace_check == 1:
                            # for (int i=0; i<5; i++) for (int j=0; j<5; j++) {t++;}
                            end = j
                            break
                        elif tokens[j][1] == "SEMI":
                            # for (int i=0; i<5; i++) for (int j=0; j<5; j++) t++;
                            # notice no braces
                            end = j
                            break

                labels.append((tokens[i][2], tokens[i][1], tokens[end][2], i)) #start event
                labels.append((tokens[end][2], tokens[i][1], i)) #end event

        if tokens[i][1] == "ID" and tokens[i+1][1] == "LPAREN":
            #solve for a function
            is_definition = 0
            paren = 0
            start = 0
            for j in range(i + 1, len(tokens)):
                paren += check_parenthesis(tokens[j])
                if tokens[j][1] == "RPAREN" and paren == 0:
                    if tokens[j+1][1] == "LBRACE":
                        is_definition = 1
                        start = j + 1
                        break
                    else:
                        break
            brace = 0
            end = 0
            for j in range(start, len(tokens)):
                if brace == 0 and tokens[j][1] == "LBRACE":
                    start = j
                brace += check_brace(tokens[j])
                if tokens[j][1] == "RBRACE" and brace == 0:
                    end = j
                    break
            if is_definition == 1:
                labels.append((tokens[start][2], "FUNCTION", tokens[end][2], start)) #start event
                labels.append((tokens[end][2], "FUNCTION", start)) #end event
            else:
                #this is a function call maybe usefull later
                pass
    labels.sort( key = lambda x: (x[0], x[-1], len(x) - 3)) #sort start/end events bj line with ends before starts
    labels_with_levels = []
    end_l = []
    for label in labels:
        if len(label) == 4: #if event start
            end_l.append(label[2])
            labels_with_levels.append((label[0], label[1] + "_" + str(len(end_l))))
        else: #if event end
            #while (label[0]>end_l[-1]):
            #    end_l.pop()
            labels_with_levels.append((label[0], label[1] + "_" + str(len(end_l))))
            if label[0] == end_l[-1]:
                end_l.pop()
    return labels_with_levels


if __name__ == '__main__':
    fname = sys.argv[1]
    lab = lex_and_label(fname)
    pom = fname.split("/")
    pom[-2] = "output"
    fname = "/".join(pom[-2:])
    f = open(fname + ".labels","w")
    for l in lab:
         f.write(str(l) + "\n")
    f.close()
