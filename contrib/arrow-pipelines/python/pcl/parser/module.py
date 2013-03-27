from entity import Entity

class Module(Entity):
    def __init__(self, filename, lineno, imports, component_definition):
        Entity.__init__(self, filename, lineno)
        self.imports = imports
        self.definition = component_definition

    def accept(self, visitor):
        visitor.visit(self)
        for an_import in self.imports:
            an_import.accept(visitor)
        self.definition.accept(visitor)

    def __str__(self):
        return "<Module:\n\timports = %s,\n\tdefinition = [%s],\n\tentity = [%s]>" % \
               (self.imports, self.definition, super(Module, self).__str__())
