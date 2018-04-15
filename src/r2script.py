import r2pipe
import re

def disassemble(start_adr,length,fname):
    print (start_adr,length,fname)
    in_re = re.compile("  +")
    end_re = re.compile(";.*")
    r2 = r2pipe.open("input/A21.out")
    r2.cmd("s "+str(start_adr))
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
        values.append((int(formated[0], 16), hex(int(formated[1], 16)), formated[2] ))
    return values
