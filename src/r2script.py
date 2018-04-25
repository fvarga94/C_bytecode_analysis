import r2pipe
import re

def disassemble(start_adr,length,fname):
    base=0
    set_base=""
    start_adr=int(start_adr,16)
    if fname.split(".")[1]=="o":
        base=0x08000040
        set_base="-B 0x08000000"
    print ("Dissasembling: ",hex(start_adr),length,fname)
    in_re = re.compile("  +")
    end_re = re.compile(";.*")
    r2 = r2pipe.open(fname,[set_base])
    r2.cmd("s "+hex(start_adr+base))
    print (hex(start_adr+base))
    output = r2.cmd("pD "+str(length))
    #print (output)
    values = []
    for o in output.split("\n"):
        start=o.find("0x")
        o=o[start:]
        if start==-1:
            continue
        formated = re.sub(end_re, "", re.sub( in_re, "\t", o)).split("\t")[:3]
        if formated[1][-1] == ".":
            formated[1]=formated[1][:-1]
        values.append((int(formated[0], 16)-base, hex(int(formated[1], 16)), formated[2] ))
    return values
