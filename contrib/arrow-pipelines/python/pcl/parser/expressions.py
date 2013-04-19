from entity import Entity

class Literal(Entity):
    def __init__(self, filename, lineno, value):
         Entity.__init__(self, filename, lineno)
         self.value = value

    def __str__(self):
        return "<Literal: value = [%s], entity = %s>" % \
               (self.value, super(Literal, self).__str__())

class Identifier(Entity):
    def __init__(self, filename, lineno, identifier):
        Entity.__init__(self, filename, lineno)
        self.identifier = identifier

    def __str__(self):
         return "<Identifier: identifier = [%s], entity = %s>" % \
                (self.identifier, super(Identifier, self).__str__())

class IdentifierCollection(Entity):
    def __init__(self, filename, lineno, identifier_collection):
        Entity.__init__(self, filename, lineno)
        self.collection = identifier_collection

    def __str__(self):
        return "<IdentifierCollection: collection = %s, entity = %s>" % \
               (self.collection, super(IdentifierCollection, self).__str__())

class Expression(Entity):
    def __init__(self, filename, lineno):
        Entity.__init__(self, filename, lineno)

class UnaryExpression(Expression):
     def __init__(self, filename, lineno, expression):
        Entity.__init__(self, filename, lineno)
        self.expression = expression

class BinaryExpression(Expression):
    def __init__(self, filename, lineno, left_expr, right_expr):
        Entity.__init__(self, filename, lineno)
        self.left = left_expr
        self.right = right_expr

class CompositionExpression(BinaryExpression):
    def __init__(self, filename, lineno, left_expr, right_expr):
        BinaryExpression.__init__(self, filename, lineno, left_expr, right_expr)

class ParallelWithTupleExpression(BinaryExpression):
     def __init__(self, filename, lineno, left_expr, right_expr):
        BinaryExpression.__init__(self, filename, lineno, left_expr, right_expr)

class ParallelWithScalarExpression(BinaryExpression):
     def __init__(self, filename, lineno, left_expr, right_expr):
        BinaryExpression.__init__(self, filename, lineno, left_expr, right_expr)

class FirstExpression(UnaryExpression):
    def __init__(self, filename, lineno, expr):
        UnaryExpression.__init__(self, filename, lineno, expr)

class SecondExpression(UnaryExpression):
    def __init__(self, filename, lineno, expr):
        UnaryExpression.__init__(self, filename, lineno, expr)

class SplitExpression(Expression):
    def __init__(self, filename, lineno):
        Expression.__init__(self, filename, lineno)

class MergeExpression(Expression):
    def __init__(self, filename, lineno, merge_mapping):
        Expression.__init__(self, filename, lineno)
        self.mapping = merge_mapping

class WireExpression(Expression):
    def __init__(self, filename, lineno, wire_mapping):
        Expression.__init__(self, filename, lineno)
        self.mapping = wire_mapping

class IdentifierExpression(Expression):
    def __init__(self, filename, lineno, identifier):
        Expression.__init__(self, filename, lineno)
        self.identifier = identifier

class LiteralExpression(Expression):
    def __init__(self, filename, lineno, literal):
        Expression.__init__(self, filename, lineno)
        self.literal = literal

