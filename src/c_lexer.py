#!/usr/bin/env python3
from pycparser.c_lexer import CLexer
import sys
import re
import subprocess

#clang -Xclang -dump-tokens code.c
#gcc -fpreprocessed -E -dD code.c

class LEX(object):
	'''
	Wraper function for the c_lexer class found in the pycparser package.
	Allows for lexical parsing of .c type files.
	'''
	def __init__(self):
		#list of scope identifier:type dictionaries
		self._scope_stack=[dict()]

	def _is_type_in_scope(self,name):
		#searche scope for the identifier type
		for scope in reversed(self._scope_stack):
			in_scope = scope.get(name)
			if in_scope is not None:
				return in_scope
		return False

	def _push_scope(self):
		#new scope caused by encapsulation
		self._scope_stack.append(dict())

	def _pop_scope(self):
		#end scope caused by encapsulation
		assert len(self._scope_stack)>1
		self._scope_stack.pop()

	def _lex_error_func(self, msg, line, column):
		#used for the compiler, not implemented since we only lex compilable code
		print ("----------------",msg, line, column)
		pass

	def _lex_on_lbrace_func(self):
		#open encapsulation
	    self._push_scope()

	def _lex_on_rbrace_func(self):
		#close encapsulation
	    self._pop_scope()

	def _lex_type_lookup_func(self, name):
		#lookup the type of the identifier
		is_type = self._is_type_in_scope(name)
		return is_type

	def lex(self, filename):
		#lex the input file

		#read the file and remove processor instructions
		completed=subprocess.run(["gcc", "-fpreprocessed", "-E","-dD",filename], stdout=subprocess.PIPE, universal_newlines=True)
		text=completed.stdout.split('\n')
		num=[]
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
				if text[i][-1]=="\\":
					hard_remove=1
				check=text[i].split(" ")
				if len(check)==3 and check[2]=='"'+filename+'"':
					number=int(check[1])
					num.append((i,number-1))
				text[i]=""
		#print (num)
		added=0
		for i in range(len(num)):
			add=num[i][1]-num[i][0]-added-1
			#print (num[i][0],num[i][1],add,added+num[i][0])
			for j in range(add):
				text.insert(num[i][0]+added,"")
			added+=add
		#print (repr(text[1664]))
		#f = open(filename, errors="replace")
		#text1 = f.readlines()
		#print (len(text),len(text1))
		#print (text[2252])
		#remove=0
		#hard_remove=0
		#pattern='^[^\']*"(\\\\.|[^"])*[^\']*"$'
		pattern='\\\\.(\\\\.)*'

		print (pattern)
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
			print (i,text[i])
		#for i in range(len(text)):
		#	if i>1660 and i<1670:
		#		print (i,text[i])
		text = "\n".join(text)
		#f.close()

		self._scope_stack=[dict()] #open new scope list

		#construct new lexer using the pycparser implementation
		lex = CLexer(self._lex_error_func, self._lex_on_lbrace_func\
					,self._lex_on_rbrace_func, self._lex_type_lookup_func)

		#initiate the lexer
		lex.build()

		lex.input(text)

		list_of_tokens = []
		while 1:
			tok = lex.token()
			if not tok:
				break
			list_of_tokens.append((tok.value, tok.type,
								   tok.lineno, lex.filename,
								   tok.lexpos))
			#print (tok)
		return list_of_tokens

if __name__ == "__main__":
	#tester for the lexer
	# requires the location of the .c file to be parsed from commandline
	filename = sys.argv[1]
	lexer = LEX()
	lot = lexer.lex(filename)
	fname = filename
	pom = fname.split("/")
	pom[-2] = "output"
	fname = "/".join(pom[-2:])
	f = open(fname+'.lexed','w')
	for tok in lot:
		f.write(str([t for t in tok])+"\n")
	f.close()
	print ("output writen to: "+fname+'.lexed')
