from entity import Entity

class Component(Entity):
    def __init__(self,
                 filename,
                 lineno,
                 name,
                 inputs,
                 outputs,
                 configuration,
                 declarations,
                 definition):
        Entity.__init__(self, filename, lineno)
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.configuration = configuration
        self.declarations = declarations
        self.definition = definition

    def accept(self, visitor):
        visitor.visit(self)
        self.definition.accept(visitor)

    def __str__(self):
        return "<Component:\n\tname = [%s],\n\tinputs = %s,\n\toutputs = %s,\n\tconfiguration = %s,\n\tdeclarations = %s\n\tdefinition = %s>" % \
               (self.name, self.inputs, self.outputs, self.configuration, self.declarations, self.definition)
