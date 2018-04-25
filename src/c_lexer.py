#!/usr/bin/env python3
from pycparser.c_lexer import CLexer
import sys

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
		f = open(filename)
		text = f.readlines()
		remove=0
		for i in range(len(text)):
			text[i]=text[i].lstrip()
			if text[i]=="":
				text[i]="\n"
			if remove==1:
				if text[i].find("*/")!=-1:
					remove=0
					text[i]=text[i][text[i].find("*/")+2:]
				else:
					text[i]="\n"
			if text[i][0] == "#" or (text[i].find("//")==0):
				text[i] = "\n"
			if text[i].find("/*")!=-1:
				if text[i].find("*/")==-1:
					remove=1
					text[i]=text[i][:text[i].find("/*")]+"\n"
				else:
					text[i]=text[i]=text[i][:text[i].find("/*")]+text[i][text[i].find("*/")+2:]

		#for t in  text:
		#	print (t)
		text = "".join(text)
		f.close()

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
