from entity import Entity

class Literal(Entity):
    def __init__(self, filename, lineno, value):
         Entity.__init__(self, filename, lineno)
         self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "<Literal: value = [%s], entity = %s>" % \
               (self.value, super(Literal, self))

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if not isinstance(other, Literal):
            return False
        return self.value == other.value

class Identifier(Entity):
    def __init__(self, filename, lineno, identifier):
        Entity.__init__(self, filename, lineno)
        self.identifier = identifier

    def __str__(self):
        return str(self.identifier)

    def __repr__(self):
        return "<Identifier: identifier = [%s], entity = %s>" % \
               (self.identifier, super(Identifier, self))

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        if not isinstance(other, Identifier):
            return False
        return self.identifier == other.identifier

class IdentifierCollection(Entity):
    def __init__(self, filename, lineno, identifier_collection):
        Entity.__init__(self, filename, lineno)
        self.collection = identifier_collection

    def __str__(self):
        return str([str(e) for e in self.collection])

    def __repr__(self):
        return "<IdentifierCollection: collection = %s, entity = %s>" % \
               (self.collection, super(IdentifierCollection, self))

    def __hash__(self):
        return hash(self.collection)

    def __eq__(self, other):
        if not isinstance(other, IdentifierCollection):
            return False
        return self.colleciton == other.collection

class Expression(Entity):
    def __init__(self, filename, lineno):
        Entity.__init__(self, filename, lineno)

    def accept(self, visitor):
        visitor.visit(self)

class UnaryExpression(Expression):
     def __init__(self, filename, lineno, expression):
        Entity.__init__(self, filename, lineno)
        self.expression = expression

     def accept(self, visitor):
         visitor.visit(self)
         self.expression.accept(visitor)

class BinaryExpression(Expression):
    def __init__(self, filename, lineno, left_expr, right_expr):
        Entity.__init__(self, filename, lineno)
        self.left = left_expr
        self.right = right_expr

    def accept(self, visitor):
        visitor.visit(self)
        self.left.accept(visitor)
        self.right.accept(visitor)

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

    def accept(self, visitor):
        visitor.visit(self)
        for merge_map in self.mapping:
            merge_map.accept(visitor)

class WireExpression(Expression):
    def __init__(self, filename, lineno, wire_mapping):
        Expression.__init__(self, filename, lineno)
        self.mapping = wire_mapping

    def accept(self, visitor):
        visitor.visit(self)
        for map_ in self.mapping:
            map_.accept(visitor)

class IdentifierExpression(Expression):
    def __init__(self, filename, lineno, identifier):
        Expression.__init__(self, filename, lineno)
        self.identifier = identifier

    def accept(self, visitor):
        visitor.visit(self)

class LiteralExpression(Expression):
    def __init__(self, filename, lineno, literal):
        Expression.__init__(self, filename, lineno)
        self.literal = literal

    def accept(self, visitor):
        visitor.visit(self)
