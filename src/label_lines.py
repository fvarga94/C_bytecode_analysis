#!/usr/bin/env python3
from pyelfaddr2line import addr2line
from labels_with_lex import lex_and_label
import sys
import copy

def label_lines(fname, src):
        text = addr2line(fname)
        files = []
        adr_dict = {}
        func_list = []
        for line in text:
            line = line.strip()
            addrlbl = line.split("\t")
            if addrlbl[0] == "---" :
                func_list.append(str(addrlbl[2]))
                adr_dict[str(addrlbl[2])]=[]
                continue
            if addrlbl[0] == "":
                continue
            adr_dict[func_list[-1]].append(addrlbl)
            if addrlbl[4] not in files:
                files.append(addrlbl[4])
        lbs = {}
        opn = [] #open
        for f_name in files:
            pom = lex_and_label(f_name,src)
            lbs[f_name] = {}
            start = int(pom[0][0])
            for y in pom[0][1:]:
                opn.append(y)
            for x in pom[1:]:
                end = int(x[0])
                for i in range(start, end + 1):
                    if str(i) not in lbs[f_name]:
                        lbs[f_name][str(i)] = "\t".join(opn)
                    elif len(opn) > len(lbs[f_name][str(i)].split("\t")):
                        lbs[f_name][str(i)]="\t".join(opn)
                    #print (i,opn)
                for y in x[1: ]:
                    if y in opn:
                        opn.remove(y)
                    else:
                        opn.append(y)
                start=end
        for f_name in files:
            for func_dict in adr_dict:
                for addr in adr_dict[func_dict]:
                    #print (addr)
                    if addr[4] == f_name and addr[6] in lbs[f_name]:
                        #print("\t"+lbs[f_name][addr[6]])
                        addr.append(lbs[f_name][addr[6]])
        return adr_dict


if __name__ == '__main__':
    fname, src = sys.argv[1], sys.argv[2]
    adr_dict = label_lines(fname, src)
    pom=fname.split("/")
    pom[-2]="output"
    fname="/".join(pom[-2: ])

    f=open(fname+".labeled_addresses",'w')
    for func_dict in adr_dict.keys():
        f.write(("---\t" + func_dict + "\n"))
        for addr in adr_dict[func_dict]:
            #print (addr)
            f.write("\t".join(addr) + "\n")
    f.close()
