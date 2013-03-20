#
# Pipeline Creation Language Parser
#
import ply.yacc as yacc

from pcl_lexer import tokens


def p_module(p):
    'module : imports_list component_def'
    print "Imports: [%s], Component def: [%s]" % (p[1], p[2])

def p_imports_list(p):
    'imports_list : import_spec imports_list'
    pass
    
