#!/usr/bin/env python3
from pyelfaddr2line import addr2line
from labels_with_lex import lex_and_label
import sys
import copy
from elftools.common.py3compat import bytes2str

def label_lines(fname, src):
        text_addressed = addr2line(fname)
        files = []
        adr_dict = {}
        func_list = []
        length = {}
        for addrlbl in text_addressed:
            if len(addrlbl) == 2 :
                func_list.append(addrlbl[0])
                adr_dict[addrlbl[0]]=[]
                length[addrlbl[0]]=addrlbl[1]
                continue
            adr_dict[func_list[-1]].append(addrlbl)
            if addrlbl[3] not in files:
                files.append(addrlbl[3])
        lbs = {}
        opn = [] #open
        f_name_dict={}
        print (files)
        for f_name in files:
            print (f_name)
            pom,k_dict = lex_and_label(f_name,src)
            for x in k_dict.keys():
                f_name_dict[x]=k_dict[x]
            lbs[f_name] = {}
            start = int(pom[0][0])
            for y in pom[0][1:]:
                opn.append(y)
            for x in pom[1:]:
                end = int(x[0])
                for i in range(start, end + 1):
                    if str(i) not in lbs[f_name]:
                        lbs[f_name][str(i)] = "\t".join(opn)
                    elif len(opn) >= len(lbs[f_name][str(i)].split("\t")):
                        lbs[f_name][str(i)]="\t".join(opn)
                    #print (i,opn)
                for y in x[1: ]:
                    if y in opn:
                        opn.remove(y)
                    else:
                        opn.append(y)
                start=end
        cur=(None,None)
        for f_name in files:
            for func_dict in adr_dict:
                for addr in adr_dict[func_dict]:
                    if addr[3] == f_name and addr[4] in lbs[f_name]:
                        #print("\t"+lbs[f_name][addr[4]])
                        addr.append(lbs[f_name][addr[4]])
        return adr_dict, f_name_dict, length


if __name__ == '__main__':
    fname, src = sys.argv[1], sys.argv[2]

    adr_dict, f_name_dict, length = label_lines(fname, src)
    pom=fname.split("/")
    pom[-2]="output"
    fname="/".join(pom[-2: ])

    f=open(fname+".labeled_addresses",'w')
    print (adr_dict.keys())
    print (f_name_dict.keys())
    #print (len(f_name_dict.keys()))
    for func_dict in adr_dict.keys():
        dict_print=[x+","+str(f_name_dict[bytes2str(func_dict)][x]) for x in f_name_dict[bytes2str(func_dict)]]
        f.write(bytes2str(func_dict)+"\t"+\
            ":".join(dict_print)+"\t"+str(length[func_dict])+"\n")
        for addr in adr_dict[func_dict]:
            f.write('{0[0]}\t{0[1]:>18}\t{0[2]:>40}\t{0[4]:>10}\t{0[3]:>}\t{0[5]}'.format(addr)+"\n")
    f.close()
    print ("output writen to: "+fname+".labeled_addresses")
