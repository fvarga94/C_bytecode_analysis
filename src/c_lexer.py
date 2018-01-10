#!/usr/bin/env python3
from pycparser.c_lexer import CLexer
import sys
_scope_stack=[dict()]

def _is_type_in_scope(name):
	for scope in reversed(_scope_stack):
		in_scope = scope.get(name)
		if in_scope is not None: return in_scope
	return False

def _push_scope():
	_scope_stack.append(dict())

def _pop_scope():
	assert len(_scope_stack)>1
	_scope_stack.pop()

def _lex_error_func(msg, line, column):
	pass

def _lex_on_lbrace_func():
    _push_scope()

def _lex_on_rbrace_func():
    _pop_scope()

def _lex_type_lookup_func(name):
	is_type = _is_type_in_scope(name)
	return is_type

def lex(filename):
	f = open(filename)
	text=f.readlines()
	for i in range(len(text)):
		if text[i][0]=="#":
			text[i]="\n"
	text="".join(text)
	#print (text)

	lex = CLexer(_lex_error_func,_lex_on_lbrace_func,_lex_on_rbrace_func,_lex_type_lookup_func)
	lex.build()
	lex.input(text)
	f.close()
	list_of_tokens=[]
	while 1:
		tok = lex.token()
		if not tok: break
		#~ print type(tok)
		list_of_tokens.append((tok.value, tok.type, tok.lineno, lex.filename, tok.lexpos))
	return list_of_tokens

if __name__ == "__main__":
	filename = sys.argv[1]
	lot=lex(filename)
	fname=filename
	pom=fname.split("/")
	pom[0]="output"
	fname="/".join(pom)
	f=open(fname+'.lexed','w')
	for tok in lot:
		f.write(str([t for t in tok])+"\n")
	f.close()
