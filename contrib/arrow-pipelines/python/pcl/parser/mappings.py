from entity import Entity

class Mapping(Entity):
    def __init__(self, filename, lineno, from_identifier, to_identifier):
        Entity.__init__(self, filename, lineno)
        self.from_ = from_identifier
        self.to = to_identifier

    def accept(self, visitor):
        visitor.visit(self)

class TopMapping(Mapping):
    def __init__(self, filename, lineno, from_identifier, to_identifier):
        Mapping.__init__(self, filename, lineno, from_identifier, to_identifier)

class BottomMapping(Mapping):
    def __init__(self, filename, lineno, from_identifier, to_identifier):
        Mapping.__init__(self, filename, lineno, from_identifier, to_identifier)

class LiteralMapping(Entity):
    def __init__(self, filename, lineno, literal, to_identifier):
        Entity.__init__(self, filename, lineno)
        self.literal = literal
        self.to = to_identifier

    def accept(self, visitor):
        visitor.visit(self)
