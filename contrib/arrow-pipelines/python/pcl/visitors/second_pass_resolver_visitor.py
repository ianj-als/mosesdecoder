from multimethod import multimethod, multimethodclass
from parser.import_spec import Import
from parser.component import Component
from parser.declaration import Declaration
from parser.expressions import UnaryExpression, \
     BinaryExpression, \
     CompositionExpression, \
     FirstExpression, \
     SecondExpression, \
     SplitExpression
from pypeline.core.types.just import Just
from pypeline.core.types.nothing import Nothing
from first_pass_resolver_visitor import FirstPassResolverVisitor, resolve_expression_once


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

    @multimethod(CompositionExpression)
    @resolve_expression_once
    def visit(self, comp_expr):
        # Check that the composing components are output/input
        # compatible
        left_outputs = comp_expr.left.resolution_symbols['outputs']
        right_inputs = comp_expr.right.resolution_symbols['inputs']
        if left_outputs != right_inputs:
            self._errors.append("ERROR: %s at line %d attempted composition " \
                                "with incompatible components, expected %s, got %s" % \
                                (comp_expr.filename,
                                 comp_expr.lineno,
                                 left_outputs,
                                 right_inputs))

        # Update the inputs and outputs for this composed component
        comp_expr.resolution_symbols['inputs'] = comp_expr.left.resolution_symbols['inputs']
        comp_expr.resolution_symbols['outputs'] = comp_expr.right.resolution_symbols['outputs']

    def __derive_inputs(self, expr):
        return self.__walk_expression(expr.parent, expr)

    def __walk_expression(self, node, child):
        if node is None:
            return Just(set(self._module.definition.inputs))

        if isinstance(node, BinaryExpression):
            if node.left is child:
                if node.resolution_symbols.has_key('inputs') and \
                   not isinstance(node.resolution_symbols['inputs'], Nothing):
                    return node.resolution_symbols['inputs']
            elif node.right is child:
                if isinstance(node.parent, BinaryExpression):
                    if node.parent.left.resolution_symbols.has_key('outputs') and \
                       not isinstance(node.parent.left.resolution_symbols['outputs'], Nothing):
                        return node.parent.left.resolution_symbols['outputs']
                elif isinstance(node.parent, UnaryExpression):
                    if node.parent.expression.resolution_symbols.has_key('outputs') and \
                       not isinstance(node.parent.expression.resolution_symbols['outputs'], Nothing):
                        return node.parent.expression.resolution_symbols['outputs']
                else:
                    raise Exception("Node's parent of unexpected type: %s" % type(node.parent))
            else:
                raise Exception("Child is neither left or right: %s" % child.__repr__())
        elif isinstance(node, UnaryExpression):
            if node.resolution_symbols.has_key('inputs') and \
               not isinstance(node.resolution_symbols['inputs'], Nothing):
                return node.resolution_symbols['inputs']
        else:
            raise Exception("Unexpected expression type: %s" % type(node))

        return self.__walk_expression(node.parent, node)

    @multimethod(FirstExpression)
    @resolve_expression_once
    def visit(self, first_expr):
        top_inputs = first_expr.expression.resolution_symbols['inputs']
        top_outputs = first_expr.expression.resolution_symbols['outputs']

        # Derive the bottom inputs
        inputs = self.__derive_inputs(first_expr)
        print "FIRST INS: %s" % inputs
        bottom_inputs = inputs >= (lambda ins: Just(set(ins[1])) if isinstance(ins, tuple) else Just(set(ins)))

        first_expr.resolution_symbols['inputs'] = top_inputs >= (lambda tins: bottom_inputs >= \
                                                                 (lambda bins: Just((tins, bins))))
        first_expr.resolution_symbols['outputs'] = top_outputs >= (lambda touts: bottom_inputs >= \
                                                                   (lambda bouts: Just((touts, bouts))))

    @multimethod(SecondExpression)
    @resolve_expression_once
    def visit(self, second_expr):
        # Derive the top inputs
        inputs = self.__derive_inputs(second_expr)
        top_inputs = inputs >= (lambda ins: Just(set(ins[0])) if isinstance(ins, tuple) else Just(set(ins)))

        bottom_inputs = second_expr.expression.resolution_symbols['inputs']
        bottom_outputs = second_expr.expression.resolution_symbols['outputs']

        second_expr.resolution_symbols['inputs'] = top_inputs >= (lambda tins: bottom_inputs >= \
                                                                  (lambda bins: Just((tins, bins))))
        second_expr.resolution_symbols['outputs'] = top_inputs >= (lambda touts: bottom_outputs >= \
                                                                   (lambda bouts: Just((touts, bouts))))

    @multimethod(SplitExpression)
    @resolve_expression_once
    def visit(self, split_expr):
        # Derive the inputs
        inputs = self.__derive_inputs(split_expr)
        split_expr.resolution_symbols['inputs'] = inputs
        split_expr.resolution_symbols['outputs'] = inputs >= (lambda ins: Just((ins, ins)))
