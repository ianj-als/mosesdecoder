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
class ExecutorVisitor(object):
    @multimethod(Module)
    def visit(self, module):
        self.__current_module = module

    @multimethod(Import)
    def visit(self, an_import):
        print "Executing Import [%s] [%s]" % (an_import.module_name, an_import.alias)

    @multimethod(Component)
    def visit(self, component):
        print "Executing Component [%s]" % (component.name)
