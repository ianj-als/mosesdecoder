import logging
import os
import sys

from parser.pcl_lexer import PCLLexer
from parser.pcl_parser import PCLParser
from visitors.resolver_visitor import ResolverVisitor
from visitors.executor_visitor import ExecutorVisitor

logging.basicConfig(
    level = logging.DEBUG,
    filename = "pcl.log",
    filemode = "w",
    format = "%(asctime)s: %(levelname)s: %(filename)s at line %(lineno)d: %(message)s",
    datefmt='%d %b %Y %H:%M:%S'
)
logger = logging.getLogger()

def parse_component(filename):
    lexer = PCLLexer(debug = 1, debuglog = logger)
    parser = PCLParser(lexer, logger, debug = 1, write_tables = 0)
    ast = parser.parseFile(filename)

    return ast


if __name__ == '__main__':
    ast = parse_component(sys.argv[1])
    print ast

    pcl_import_path = os.getenv("PCL_IMPORT_PATH", ".")        
    resolver = ResolverVisitor(pcl_import_path)
    ast.accept(resolver)
    errors = resolver.get_errors()
    if errors:
        for error in errors:
            print error
    else:
        executor = ExecutorVisitor()
        ast.accept(executor)
