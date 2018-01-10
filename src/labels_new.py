import re
import sys
import copy

capsules=["for","while","do","if","switch","else","func"]
start_end={}

for encap in capsules:
    start_end[encap]=[]
level=0

labels=[]

def one_line_encap(pom_str,first,last,level):
    global lab,start_end
    found=0
    found_l=[]
    for encap in capsules[:-1]:
        stop=0
        found_i=0
        while(stop==0):
            k=found
            if encap in pom_str[found_i:]:
                found+=1
                found_i=pom_str.find(encap,found_i)
                found_l.append((found_i,encap))
                found_i+=2
            else:
                stop=1
            if k==found:
                stop=1
    found_l=sorted(found_l, key=lambda tup: tup[0])
    done=[0 for x in range(len(found_l))]
    for f in range(len(found_l[:-1])):
        pom_lab=[x for x in lab]
        fi=found_l[f][0]
        encap=found_l[f][1]
        start_end[encap].append([level,line_num,-1])
        pom_lab.append(encap+"_"+str(level))
        pom_lab[0]-=pom_str[pom_str.find(encap,fi)+1:].count("\n")
        labels.append(pom_lab)
        pom_lab=[x for x in lab]
        for j in range(len(start_end[encap])):
            if start_end[encap][j][0]==level and start_end[encap][j][2]==-1:
                #print (start_end[x][j])
                encap_start=fi
                encap_end=len(pom_str)
                stop=0
                while(stop==0):
                    for encap_pom in capsules[:-1]:
                        if encap_pom in pom_str[fi]:s
                nn=pom_str[pom_str.find(";",pom_str.find(")",fi)):].count("\n")
                start_end[encap][j][2]=line_num-nn
                pom_lab.append(encap+"_"+str(level))
                pom_lab[0]-=nn
        labels.append(pom_lab)
    return

def remove_strings(s):
    new,p=re.subn('(".*\[^\\]")|(\'.*\[^\\]\')','""',s)
    print (p )
    return new

def ln_set(pom_str,line_num):
    if "\n" in pom_str:
        line_num+=pom_str.count("\n")
        lab=[line_num]
        return line_num,lab

def split_and_label(fname,src=""):
    fname=src+fname
    f=open(fname,'r')
    lines=f.read()

    line_num=1
    #print (line_num)
    level=0
    lines=remove_strings(lines)
    print (lines)
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
            for encap in capsules:
                found+=pom_str.count(encap)
            if found==1:
                for encap in capsules:
                    if encap in pom_str:
                        fi=pom_str.find(encap)
                        start_end[encap].append([level,line_num,-1])
                        lab.append(encap+"_"+str(level))
                        lab[0]-=pom_str[pom_str.find(encap)+1:].count("\n")
            elif found==0:
                start_end["func"].append([level,line_num,-1])
                lab.append("func_"+str(level))
                #lab[0]-=pom_str[pom_str.find("()")+1:].count("\n")
            else:
                one_line_encap(pom_str,0,len(pom_str),level)
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
