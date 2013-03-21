class Component(object):
    def __init__(self,
                 name,
                 inputs,
                 outputs,
                 configuration,
                 declarations,
                 definition):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.configuration = configuration
        self.delcarations = declarations
        self.definition = definition

    def __str__(self):
        return "<Component: name = [%s], inputs = %s, outputs = %s, configuration = %s, def = %s>" % \
               (self.name, self.inputs, self.outputs, self.configuration, self.definition)
