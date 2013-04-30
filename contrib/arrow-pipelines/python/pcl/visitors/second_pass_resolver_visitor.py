from multimethod import multimethod, multimethodclass
from parser.import_spec import Import
from parser.component import Component
from parser.declaration import Declaration
from parser.expressions import Literal, \
     Identifier, \
     UnaryExpression, \
     CompositionExpression, \
     ParallelWithTupleExpression, \
     ParallelWithScalarExpression, \
     FirstExpression, \
     SecondExpression, \
     SplitExpression, \
     MergeExpression, \
     WireExpression, \
     WireTupleExpression, \
     IdentifierExpression, \
     LiteralExpression
from parser.mappings import Mapping, \
     TopMapping, \
     BottomMapping, \
     LiteralMapping
from parser.module import Module
from parser.helpers import parse_component
from pypeline.core.types.just import Just
from first_pass_resolver_visitor import FirstPassResolverVisitor


@multimethodclass
class SecondPassResolverVisitor(FirstPassResolverVisitor):
    def __init__(self,
                 resolver_factory,
                 pcl_import_path = [],
                 python_import_path = []):
        FirstPassResolverVisitor.__init__(self,
                                          resolver_factory,
                                          pcl_import_path,
                                          python_import_path)

    @multimethod(Module)
    def visit(self, module):
        pass

    @multimethod(Import)
    def visit(self, an_import):
        pass

    @multimethod(Component)
    def visit(self, component):
        pass

    @multimethod(Declaration)
    def visit(self, decl):
        pass

    @multimethod(object)
    def visit(self, nowt):
        # Root expression, so get inputs and outpus
        # from module defined inputs and outputs clauses
        expr = self._module.definition.definition
        expected_fn = lambda e: Just((set(e[0]), set(e[1]))) \
                      if isinstance(e, tuple) else Just(set(e))

        _ = (Just(self._module.definition.inputs) >= expected_fn) >= \
            (lambda expected_inputs: expr.resolution_symbols['inputs'] >= \
             (lambda actual_inputs: self._errors.append("ERROR: %s at line %d component " \
                                                        "expects inputs %s, but got %s" % \
                                                        (expr.filename, \
                                                         expr.lineno, \
                                                         expected_inputs, \
                                                         actual_inputs)) \
              if expected_inputs != actual_inputs else None))
        _ = (Just(self._module.definition.outputs) >= expected_fn) >= \
            (lambda expected_outputs: expr.resolution_symbols['outputs'] >= \
             (lambda actual_outputs: self._errors.append("ERROR: %s at line %d component " \
                                                         "expects outputs %s, but got %s" % \
                                                         (expr.filename, \
                                                          expr.lineno, \
                                                          expected_outputs, \
                                                          actual_outputs)) \
              if expected_outputs != actual_outputs else None))
