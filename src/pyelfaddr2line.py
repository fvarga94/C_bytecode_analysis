#!/usr/bin/env python3
#-------------------------------------------------------------------------------
# elftools example: dwarf_decode_address.py
#
# Decode an address in an ELF file to find out which function it belongs to
# and from which filename/line it comes in the original source file.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
# reconstructed some of the example tools to form this tool F.Varga
from __future__ import print_function
import sys
import r2script

# If pyelftools is not installed, the example can also run from the root or
# examples/ dir of the source distribution.
sys.path[0:0] = ['.', '..']

from elftools.common.py3compat import maxint, bytes2str
from elftools.dwarf.descriptions import describe_form_class
from elftools.elf.elffile import ELFFile


def process_file(filename, address_start, address_end, offset):
    #print('Processing file:', filename)
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        if not elffile.has_dwarf_info():
            print('  file has no DWARF info')
            return

        # get_dwarf_info returns a DWARFInfo context object, which is the
        # starting point for all DWARF-based processing in pyelftools.
        dwarfinfo = elffile.get_dwarf_info()
        ndict={}
        funcname_l = decode_funcname(dwarfinfo, address_start, address_end + 1)
        for func_name in funcname_l:
            if func_name[1] not in ndict:
                ndict[func_name[1]]=[]
                ndict[func_name[1]].append(func_name[0])
            else:
                ndict[func_name[1]].append(func_name[0])
        number_f=len(ndict.keys())
        new_output = []
        function_length={}
        function_counter=-1
        for func_name in ndict:
            function_counter+=1
            output=[]
            min_a,max_a = address_end,0
            addresses=[]
            output.append([func_name])
            for address in ndict[func_name]:
                addresses.append(address)
            print ("Processing func_name: ",func_name," i= ",function_counter," of: ", number_f)
            alf_list = decode_file_line (dwarfinfo, addresses)
            print ("End")
            for address, line, file_name in alf_list:
                if file_name == None:
                    continue
                #print('Function:', bytes2str(funcname))
                if address>max_a:
                    max_a=address
                if address<min_a:
                    min_a=address
                output.append([address, bytes2str(file_name), str(line)])
            print (func_name,hex(min_a),hex(max_a))
            sys.stderr.write("Proccessing: "+str(function_counter+1)+" / "+str(number_f)+"\n")
            fo = r2script.disassemble( hex(min_a), 1 - min_a + max_a, filename)
            i=0
            for j in range(len(output)):
                if len(output[j])==1:
                    new_output.append(output[j])
                    current=output[j][0]
                    continue
                if output[j][0]>fo[i][0]:
                    continue
                elif output[j][0] == fo[i][0]:
                    new_output.append([hex(fo[i][0]),str(fo[i][1])\
                                        ,str(fo[i][2]),output[j][1],\
                                        output[j][2]])
                    i+=1
                    if i==len(fo):
                        break
            function_length[current]=i
        for i in range(len(new_output)):
            if new_output[i][0] in function_length.keys():
                new_output[i].append(function_length[new_output[i][0]])
        return new_output



def decode_funcname(dwarfinfo, address_start, address_end):
    # Go over all DIEs in the DWARF information, looking for a subprogram
    # entry with an address range that includes the given address. Note that
    # this simplifies things by disregarding subprograms that may have
    # split address ranges.
    func_l=[]
    l=[ i for i in range(address_start, address_end) ]
    for CU in dwarfinfo.iter_CUs():
        for DIE in CU.iter_DIEs():
            try:
                if DIE.tag == 'DW_TAG_subprogram':
                    lowpc = DIE.attributes['DW_AT_low_pc'].value

                    # DWARF v4 in section 2.17 describes how to interpret the
                    # DW_AT_high_pc attribute based on the class of its form.
                    # For class 'address' it's taken as an absolute address
                    # (similarly to DW_AT_low_pc); for class 'constant', it's
                    # an offset from DW_AT_low_pc.
                    highpc_attr = DIE.attributes['DW_AT_high_pc']
                    highpc_attr_class = describe_form_class(highpc_attr.form)
                    if highpc_attr_class == 'address':
                        highpc = highpc_attr.value
                    elif highpc_attr_class == 'constant':
                        highpc = lowpc + highpc_attr.value
                    else:
                        print('Error: invalid DW_AT_high_pc class:',
                              highpc_attr_class)
                        continue
                    #print ("--------------",hex(lowpc),hex(highpc))
                    if lowpc in l and highpc in l:
                        #print ("oba")
                        for address in range(lowpc, highpc):
                            func_l.append((address, DIE.attributes['DW_AT_name'].value))
                    elif lowpc not in l and highpc in l:
                        #print ("HIGH")
                        for address in range(address_start, highpc):
                            func_l.append((address, DIE.attributes['DW_AT_name'].value))
                    elif lowpc in l and highpc not in l:
                        #print ("low")
                        for address in range(lowpc, address_end):
                            func_l.append((address, DIE.attributes['DW_AT_name'].value))
                    else:
                        pass
                        for address in range(address_start, address_end):
                            func_l.append((address, DIE.attributes['DW_AT_name'].value))
                    print("Processing:", DIE.attributes['DW_AT_name'].value)
            except KeyError:
                continue
    return func_l


def decode_file_line(dwarfinfo, addresses):
    # Go over all the line programs in the DWARF information, looking for
    # one that describes the given address.

    dfl=[] #decode file listdwarfinfo.iter_CUs()
    i=-1
    #count=0
    #count_flag=len(addresses)
    for CU in dwarfinfo.iter_CUs():
        i+=1
        # First, look at line programs to find the file/line for the address
        #print ("----",hex(addresses[-1]))
        lineprog = dwarfinfo.line_program_for_CU(CU)
        for address in addresses:
            i+=1
            prevstate = None
            for entry in lineprog.get_entries():
                # We're interested in those entries where a new state is assigned
                if entry.state is None:
                    continue
                #print ("entry ...",hex(entry.state.address))
                # Looking for a range of addresses in two consecutive states that
                # contain the required address.
                if prevstate and prevstate.address <= address < entry.state.address:
                    filename = lineprog['file_entry'][prevstate.file - 1].name
                    line = prevstate.line
                    #print (hex(address))
                    dfl.append((address, line, filename))
                    #count+=1
                prevstate = entry.state
            #if count==count_flag:
            #    break
        print ("i: ",i)
    return dfl



def get_addr(filename):
    #print('In file:', filename)
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)
        for section in elffile.iter_sections():
            if section.name.startswith('.text'):
                print (section.header["sh_name"])
                return  int(section.header["sh_offset"]),\
                        hex(section.header['sh_addr']),\
                        hex(section.header['sh_addr'] + section.data_size)

def addr2line(fname):
    offset, address_start, address_end = get_addr(fname)
    print ("Addresses gathered: ",address_start,address_end)

    return process_file(fname,
                        int(address_start, 16), int(address_end, 16),
                        offset)



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Expected usage: {0} <executable>'.format(sys.argv[0]))
        sys.exit(1)
    offset, address_start, address_end = get_addr(sys.argv[1])
    print ("Addresses gathered:", int(address_start, 16), int(address_end, 16))
    print ("Size: ",  - int(address_start, 16) + int(address_end, 16))
    output=process_file(sys.argv[1], int(address_start, 16), int(address_end, 16), offset)

    fname=sys.argv[1]
    pom=fname.split("/")
    pom[-2]="output"
    fname="/".join(pom[-2:])+".addr2line"
    f=open(fname,'w')
    for o in output:
        if len(o)==2:
            f.write('{0}\t{1}'.format(bytes2str(o[0]),o[1])+"\n")
            continue
        f.write('{0[0]}\t{0[1]:>18}\t{0[2]:>40}\t{0[4]:>10}\t{0[3]:>}'.format(o)+"\n")
    f.close()
    print ("output writen to: "+fname)
