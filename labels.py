keywords="auto break case char\
 const continue default do\
 double else enum extern\
 float for goto if\
 int long register return\
 short signed sizeof static\
 struct switch typedef union\
 unsigned void volatile while"

keywords=keywords.split(' ')
import re
import sys
import copy

capsules=["for","while","do","if","else","func"]
start_end={}

for encap in capsules:
    start_end[encap]=[]
level=0

labels=[]


def remove_strings(s):
    new,_=re.subn('(\".*\[^\\]\")|(\'.*\[^\\]\')',"\"\"",s)
    return new

def ln_set(pom_str,line_num):
    if "\n" in pom_str:
        line_num+=pom_str.count("\n")
        lab=[line_num]
        return line_num,lab

def split_and_label(fname):
    f=open(fname,'r')
    lines=f.read()

    line_num=1
    #print (line_num)
    level=0
    lines=remove_strings(lines)
    num=lines.count("{")+lines.count("}")
    start=0
    lab=[line_num]
    pom_str=""
    w=0
    for i in range(num):
        left=lines.find("{",start)
        right=lines.find("}",start)
        if (left!=-1 and left<=right):
            level+=1
            if w==1:
                start+=lines[start:].find("while")+4
                w=0
            pom_str=lines[start:left]
            line_num,lab=ln_set(pom_str,line_num)
            found=0
            for encap in capsules[0:-1]:
                if encap in pom_str:
                    found=1
                    start_end[encap].append([level,line_num,-1])
                    lab.append(encap+"_"+str(level))
                    lab[0]-=pom_str[pom_str.find(encap)+1:].count("\n")
            if not found:
                start_end["func"].append([level,line_num,-1])
                lab.append("func_"+str(level))
                #lab[0]-=pom_str[pom_str.find("()")+1:].count("\n")

            start=left+1

        elif right!=-1:
            if w==1:
                start+=lines[start:].find("while")+4
                w=0
            pom_str=lines[start:right]
            line_num,lab=ln_set(pom_str,line_num)
            #print (pom_str,line_num)
            for encap in capsules:
                for j in range(len(start_end[encap])):
                    if start_end[encap][j][0]==level and start_end[encap][j][2]==-1:
                        #print (start_end[x][j])
                        start_end[encap][j][2]=line_num
                        lab.append(encap+"_"+str(level))
                        if encap=="do":
                            w=1
            start=right+1
            level-=1
        labels.append(lab)

    #print (start_end)
    return labels

if __name__ == '__main__':
    fname=sys.argv[1]
    lbs=split_and_label(fname)
    fname=sys.argv[1]
    pom=fname.split("/")
    pom[0]="output"
    fname="/".join(pom)
    f=open(fname+".labels",'w')
    for l in lbs:
        for label in l:
            f.write(str(label)+"\t")
        f.write("\n")
