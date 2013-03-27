import glob
import os

from multimethod import multimethod, multimethodclass
from parser.import_spec import Import
from parser.component import Component
from parser.declaration import Declaration
from parser.expressions import Literal, \
     Identifier, \
     CompositionExpression, \
     ParallelWithTupleExpression, \
     ParallelWithScalarExpression, \
     FirstExpression, \
     SecondExpression, \
     SplitExpression, \
     MergeExpression, \
     WireExpression, \
     IdentifierExpression, \
     LiteralExpression
from parser.mappings import Mapping, \
     TopMapping, \
     BottomMapping, \
     LiteralMapping
from parser.module import Module


@multimethodclass
class ResolverVisitor(object):
    def __init__(self, pcl_import_path = []):
        if pcl_import_path:
            self.__import_paths = pcl_import_path.split(";")
        else:
            self.__import_paths = ["."]
        self.__errors = []

    @staticmethod
    def __build_module_filename(identifier):
        split_identifier = identifier.identifier.split('.')
        if len(split_identifier) == 1:
            module_filename = split_identifier[0]
        else:
            module_filename = os.path.join(os.path.join(*split_identifier[:-1]),
                                           split_identifier[-1])

        return module_filename + ".[Pp][Cc][Ll]"

    def get_errors(self):
        return tuple(self.__errors)

    @multimethod(Module)
    def visit(self, module):
        self.__current_module = module

    @multimethod(Import)
    def visit(self, an_import):
        module_filename = ResolverVisitor.__build_module_filename(an_import.module_name)
        files = reduce(lambda x, y: x + y,
                       [glob.glob(os.path.join(directory, module_filename))
                        for directory in self.__import_paths])

        if files:
            pass
        else:
            self.__errors.append("ERROR: %s at line %d, module %s not found" % \
                                 (an_import.filename,
                                  an_import.lineno,
                                  an_import.module_name.identifier))

        print "Import [%s] [%s]" % (an_import.module_name, an_import.alias)

    @multimethod(Component)
    def visit(self, component):
        print "Component [%s]" % (component.name)
