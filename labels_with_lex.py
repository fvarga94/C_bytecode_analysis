import re
import sys
import copy
from c_lexer import lex

k_words=["FOR","WHILE","DO","IF","SWITCH","ELSE"]

def lex_and_label(fname,src=""):
    tokens=lex(src+fname)
    labels=[]
    do_check=0
    for i in range(len(tokens)):
        #print (tokens[i])
        if tokens[i][1] in k_words:
            #SOLVE capsules
            if tokens[i][1]=="DO":
                do_check=1
            if tokens[i][1]=="WHILE" and do_check==1:
                do_check=0
                continue
            is_encapsulating=0
            paren=0
            start=i+1
            if tokens[i+1][1]=="LBRACE":
                #print ("CHECK",tokens[i])
                is_encapsulating=1
            else:
                for j in range(i+1,len(tokens)):
                    #print (tokens[i][1],tokens[j][1])
                    if tokens[j][1]=="LPAREN":
                        paren+=1
                    elif tokens[j][1]=="RPAREN":
                        paren-=1
                    if tokens[j][1]=="RPAREN" and paren==0:
                        #print ("CHECK",tokens[j+1][1])
                        if tokens[j+1][1]=="LBRACE":
                            #print ("Yes")
                            is_encapsulating=1
                            start=j+1
                            break
                        else:
                            break
            if is_encapsulating==1:
                brace=0
                end=0
                for j in range(start,len(tokens)):
                    if tokens[j][1]=="LBRACE":
                        brace+=1
                    elif tokens[j][1]=="RBRACE":
                        brace-=1
                    if tokens[j][1]=="RBRACE" and brace==0:
                        end=j
                        break
                labels.append((tokens[i][2],tokens[i][1],tokens[end][2]))
                labels.append((tokens[end][2],tokens[i][1]))
                #print (tokens[i],tokens[end])
            else:
                end=0
                paren=0
                brace=0
                brace_check=0
                for j in range(start,len(tokens)):
                    if tokens[j][1]=="LBRACE":
                        if brace_check==brace:
                            brace_check+=1
                        brace+=1
                    elif tokens[j][1]=="RBRACE":
                        brace-=1
                    elif tokens[j][1]=="RPAREN":
                        paren-=1
                    elif tokens[j][1]=="LPAREN":
                        paren+=1
                    if brace==0 and paren==0:
                        if brace_check==1:
                            end=j
                            break
                        elif tokens[j][1]=="SEMI":
                            end=j
                            break
                labels.append((tokens[i][2],tokens[i][1],tokens[end][2]))
                labels.append((tokens[end][2],tokens[i][1]))
                #print (tokens[i],tokens[end])


        if tokens[i][1]=="ID" and tokens[i+1][1]=="LPAREN":
            #solve if function
            #print (tokens[i])
            is_definition=0
            paren=0
            start=0
            for j in range(i+1,len(tokens)):
                #print (tokens[i][1],tokens[j][1])
                if tokens[j][1]=="LPAREN":
                    paren+=1
                elif tokens[j][1]=="RPAREN":
                    paren-=1
                if tokens[j][1]=="RPAREN" and paren==0:
                    #print ("CHECK",tokens[j+1][1])
                    if tokens[j+1][1]=="LBRACE":
                        #print ("Yes")
                        is_definition=1
                        start=j+1
                        break
                    else:
                        break
            brace=0
            end=0
            for j in range(start,len(tokens)):
                if tokens[j][1]=="LBRACE":
                    if brace==0:
                        start=j
                    brace+=1
                elif tokens[j][1]=="RBRACE":
                    brace-=1
                if tokens[j][1]=="RBRACE" and brace==0:
                    end=j
                    break
            if is_definition==1:
                labels.append((tokens[start][2],"FUNCTION",tokens[end][2]))
                labels.append((tokens[end][2],"FUNCTION"))
                #print (tokens[i],tokens[i+1],tokens[end])
            else:
                #this is a function call maybe usefull later
                pass
    labels=sorted(labels)
    labels_with_levels=[]
    end_l=[]
    for label in labels:
        if len(label)==3:
            end_l.append(label[2])
            labels_with_levels.append((label[0],label[1]+"_"+str(len(end_l))))
            #print (end_l)
        else:
            while (label[0]>end_l[-1]):
                end_l.pop()
            labels_with_levels.append((label[0],label[1]+"_"+str(len(end_l))))
            if label[0] == end_l[-1]:
                end_l.pop()
    return labels_with_levels


if __name__ == '__main__':
    fname=sys.argv[1]
    lab=lex_and_label(fname)
    pom=fname.split("/")
    pom[-2]="output"
    fname="/".join(pom[-2:])
    f=open(fname+".labels","w")
    for l in lab:
         f.write(str(l)+"\n")
    f.close()
