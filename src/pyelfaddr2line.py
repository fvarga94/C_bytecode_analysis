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

# If pyelftools is not installed, the example can also run from the root or
# examples/ dir of the source distribution.
sys.path[0:0] = ['.', '..']

from elftools.common.py3compat import maxint, bytes2str
from elftools.dwarf.descriptions import describe_form_class
from elftools.elf.elffile import ELFFile


def process_file(filename, address1,address2,ofs):
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
            #print (address)
            #address=address2
        funcname_l = decode_funcname(dwarfinfo, address1,address2+1)

        for funcname in funcname_l:
            if funcname[1] not in ndict:
                ndict[funcname[1]]=[]
                ndict[funcname[1]].append(funcname[0])
            else:
                ndict[funcname[1]].append(funcname[0])
        output=[]
        for funcname in ndict:
            output.append('---\tFunc:\t'+bytes2str(funcname)+"\n")
            addresses=[]
            for address in ndict[funcname]:
                addresses.append(address)
            alf_list = decode_file_line(dwarfinfo, addresses)
            for address,line,file in alf_list:
                if file==None:
                    continue
                #print('Function:', bytes2str(funcname))
                output.append('-\tAddr:\t'+str(address-address1+ofs)+\
                '\tFile:\t'+bytes2str(file)+\
                '\tLine:\t'+str(line)+"\n")
        return output



def decode_funcname(dwarfinfo, address1, address2):
    # Go over all DIEs in the DWARF information, looking for a subprogram
    # entry with an address range that includes the given address. Note that
    # this simplifies things by disregarding subprograms that may have
    # split address ranges.
    func_l=[]
    l=[i for i in range(address1,address2)]
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
                    if lowpc in l and highpc in l:
                        for address in range(lowpc,highpc):
                            func_l.append((address,DIE.attributes['DW_AT_name'].value))
                    elif lowpc not in l and highpc in l:
                        for address in range(address1,highpc):
                            func_l.append((address,DIE.attributes['DW_AT_name'].value))
                    elif lowpc in l and highpc not in l:
                        for address in range(lowpc,address2):
                            func_l.append((address,DIE.attributes['DW_AT_name'].value))
                    else:
                        pass
                        for address in range(address1,address2):
                            func_l.append((address,DIE.attributes['DW_AT_name'].value))
                    print("Processing:",DIE.attributes['DW_AT_name'].value)
            except KeyError:
                continue
    return func_l


def decode_file_line(dwarfinfo, addresses):
    # Go over all the line programs in the DWARF information, looking for
    # one that describes the given address.
    dfl=[]
    for CU in dwarfinfo.iter_CUs():
        # First, look at line programs to find the file/line for the address

        for address in addresses:
            lineprog = dwarfinfo.line_program_for_CU(CU)
            prevstate = None
            for entry in lineprog.get_entries():
                # We're interested in those entries where a new state is assigned
                if entry.state is None or entry.state.end_sequence:
                    continue
                # Looking for a range of addresses in two consecutive states that
                # contain the required address.

                if prevstate and prevstate.address <= address < entry.state.address:
                    filename = lineprog['file_entry'][prevstate.file - 1].name
                    line = prevstate.line
                    dfl.append((address,line,filename))
                    if address%100==0:
                        print (dfl[-1])
                prevstate = entry.state
    return dfl



def get_addr(filename):
    #print('In file:', filename)
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)
        for section in elffile.iter_sections():
            if section.name.startswith('.text'):
                return section.header["sh_offset"],hex(section.header['sh_addr']),hex(section.header['sh_addr']+section.data_size)

def addr2line(fname):
    ofs,addr1,addr2=get_addr(fname)
    print ("Addresses gathered.")
    return process_file(fname, int(addr1,16), int(addr2,16),ofs)



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Expected usage: {0} <executable>'.format(sys.argv[0]))
        sys.exit(1)
    ofs,addr1,addr2=get_addr(sys.argv[1])
    print ("Addresses gathered:", int(addr1,16), int(addr2,16))
    output=process_file(sys.argv[1], int(addr1,16), int(addr2,16),ofs)
    fname=sys.argv[1]
    pom=fname.split("/")
    pom[-2]="output"
    fname="/".join(pom[-2:])
    f=open(fname+".addr2line",'w')
    for o in output:
        f.write(o)
    f.close()
