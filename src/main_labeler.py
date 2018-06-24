#!/usr/bin/env python3
from pyelfaddr2line import addr2line
from labels_with_lex import lex_and_label
import sys
import copy
import re
import subprocess
from elftools.common.py3compat import bytes2str

def process_text(fname, src, fname_src):
	#read the file and remove processor instructions
    completed=subprocess.run(["find",fname_src,"-name",fname], stdout=subprocess.PIPE, universal_newlines=True)
    source_files=completed.stdout.split('\n')
    if len(source_files)==1:
        completed=subprocess.run(["find",src,"-name",fname], stdout=subprocess.PIPE, universal_newlines=True)
        source_files=completed.stdout.split('\n')
    if len(source_files)==1:
        completed=subprocess.run(["find","/usr/include/","-name",fname], stdout=subprocess.PIPE, universal_newlines=True)
        source_files=completed.stdout.split('\n')
    if len(source_files)>2:
        return None,None
    print (source_files)
    filename=source_files[0]
    completed=subprocess.run(["gcc", "-fpreprocessed", "-E","-dD",source_files[0]], stdout=subprocess.PIPE, universal_newlines=True)
    text=completed.stdout.split('\n')
    num=[]
    ignore_list=[]
    del text[-1]
    hard_remove=0
    for i in range(len(text)):
        text[i]=text[i].lstrip()
        if hard_remove==1:
            if text[i][-1]=="\\":
                hard_remove+=1
            text[i]=""
            hard_remove-=1

        if len(text[i])!=0 and text[i][0]=='#':
            if "#define" in text[i]:
                pom=text[i].split(" ")[1]
                if "(" in pom:
                    pom=pom[:pom.find("(")]
                ignore_list.append(pom)
            if text[i][-1]=="\\":
                hard_remove=1
            check=text[i].split(" ")
            #print ("----------------",check,filename)
            if len(check)==3 and check[2]=='"'+filename+'"':
                number=int(check[1])
                num.append((i,number-1))
            text[i]=""
    print (num)
    added=0
    if num[0]==(0,0):
        del text[0]
        added=-1
    for i in range(len(num)):
        add=num[i][1]-num[i][0]-added-1
        #print (num[i][0],num[i][1],add,added+num[i][0])
        if add==-1:
            continue
        for j in range(add):
            text.insert(num[i][0]+added,"")
        added+=add
	#print (repr(text[1664]))
	#f = open(filename, errors="replace")
	#text1 = f.readlines()
	#for i in range(len(text)):
	#	print (i,text[i],i,text1[i])
	#print (len(text),len(text1))
	#print (text[2252])
	#remove=0
	#hard_remove=0
	#pattern='^[^\']*"(\\\\.|[^"])*[^\']*"$'
    pattern='\\\\.(\\\\.)*'

	#print (pattern)
    regsub=re.compile(pattern)
	#for i in range(len(text1)):
	#	print (i,text1[i],i,text[i])
    for i in range(len(text)):
	#	text[i]=text[i].lstrip()
	#	if text[i]=="":
	#		text[i]="\n"
		#if remove==1:
		#	if text[i].find("*/")!=-1:
		#		remove=0
		#		text[i]=text[i][text[i].find("*/")+2:]
		#	else:
		#		text[i]="\n"
		#if hard_remove==1:
		#	if text[i][-2:]=="\\\n":
		#		hard_remove+=1
		#	text[i]="\n"
		#	hard_remove-=1
		#if text[i][0] == "#" or (text[i].find("//")==0):
		#	if text[i][-2:]=="\\\n":
		#		hard_remove=1
		#	text[i] = "\n"
		#n=text[i].find("/*")
		#m=text[i].find("'")
		#g=text[i].find("\"")
		#if n!=-1 and (m>n or m==-1) and (g>n or g==-1):
		#	if text[i].find("*/")==-1:
		#		remove=1
		#		text[i]=text[i][:text[i].find("/*")]+"\n"
		#	else:
		#		text[i]=text[i]=text[i][:text[i].find("/*")]+text[i][text[i].find("*/")+2:]
        text[i]=re.sub(regsub,"\g<1> ",text[i])
		#print (i,text[i])
	#for i in range(len(text)):
	#	if i>1660 and i<1670:
	#		print (i,text[i])
    text = "\n".join(text)
	#f.close()
    return text, ignore_list

def label_lines(fname, src, fname_src):
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
        ig_list=[]
        text=dict()
        for f_name in files:
            pom0, pom1 = process_text(f_name, src, fname_src)
            if pom0 != None and pom1!=None:
                text[f_name]=pom0
                ig_list.extend(pom1)
        print ("------------- ig_list:")
        print (ig_list)
        for f_name in files:
            print (f_name)
            if f_name not in text:
                continue
            sys.stderr.write("Lexing: "+f_name+"\n")
            pom,k_dict = lex_and_label(f_name,text[f_name], ig_list)
            if pom==None or k_dict==None:
                continue
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
            if f_name not in lbs:
                continue
            for func_dict in adr_dict:
                for addr in adr_dict[func_dict]:
                    if addr[3] == f_name and addr[4] in lbs[f_name]:
                        #print("\t"+lbs[f_name][addr[4]])
                        addr.append(lbs[f_name][addr[4]])
        return adr_dict, f_name_dict, length


if __name__ == '__main__':
    fname, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
    if out=="none":
        out=""
    pom=fname.split("/")
    fname_src="/".join(pom[:-1 ])
    pom[-2]="output"+out
    #sys.stderr.write(fname_src+"\n")
    adr_dict, f_name_dict, length = label_lines(fname, src, fname_src)

    fname_src="/".join(pom[:-1 ])
    fname="/".join(pom[-2: ])

    f=open(fname+".labeled_addresses",'w')
    print (adr_dict.keys())
    print (f_name_dict.keys())
    #print (len(f_name_dict.keys()))
    for func_dict in adr_dict.keys():
        if bytes2str(func_dict) not in f_name_dict:
            continue
        flag=0
        for addr in adr_dict[func_dict]:
            if len(addr)<6:
                flag=1
        if flag==1:
            continue
        dict_print=[x+","+str(f_name_dict[bytes2str(func_dict)][x]) for x in f_name_dict[bytes2str(func_dict)]]
        f.write(bytes2str(func_dict)+"\t"+\
            ":".join(dict_print)+"\t"+str(length[func_dict])+"\n")
        for addr in adr_dict[func_dict]:
            f.write('{0[0]}\t{0[1]:>18}\t{0[2]:>40}\t{0[4]:>10}\t{0[3]:>}\t{0[5]}'.format(addr)+"\n")
    f.close()
    print ("output writen to: "+fname+".labeled_addresses")
