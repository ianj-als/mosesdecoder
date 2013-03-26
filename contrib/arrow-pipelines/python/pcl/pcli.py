import logging
import sys

from parser.pcl_lexer import PCLLexer
from parser.pcl_parser import PCLParser

logging.basicConfig(
    level = logging.DEBUG,
    filename = "pcl.log",
    filemode = "w",
    format = "%(asctime)s: %(filename)s at line %(lineno)4d: %(message)s",
    datefmt='%m/%d/%Y %H:%M:%S'
)
logger = logging.getLogger()

lexer = PCLLexer(debug = 1, debuglog = logger)
parser = PCLParser(lexer, logger, debug = 1)

ast = parser.parseFile(sys.argv[1])
if ast:
    print "Imports: [%s], Component def: [%s]" % \
          (", ".join([str(e) for e in ast['imports']]), ast['definition'])
