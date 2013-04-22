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
        print "Executing Component [%s]" % (component.identifier)

    @multimethod(CompositionExpression)
    def visit(self, comp_expr):
        pass

    @multimethod(ParallelWithTupleExpression)
    def visit(self, para_tuple_expr):
        pass

    @multimethod(ParallelWithScalarExpression)
    def visit(self, para_scalar_expr):
        pass

    @multimethod(FirstExpression)
    def visit(self, first_expr):
        pass

    @multimethod(SecondExpression)
    def visit(self, second_expr):
        pass

    @multimethod(SplitExpression)
    def visit(self, split_expr):
        pass

    @multimethod(MergeExpression)
    def visit(self, merge_expr):
        pass

    @multimethod(WireExpression)
    def visit(self, wire_expr):
        pass

    @multimethod(IdentifierExpression)
    def visit(self, iden_expr):
        pass

    @multimethod(LiteralExpression)
    def visit(self, literal_expr):
        pass
