from entity import Entity

class Declaration(Entity):
    def __init__(self, filename, lineno, identifier, component_alias, configuration_mappings):
        Entity.__init__(self, filename, lineno)
        self.identifier = identifier
        self.component_alias = component_alias
        self.configuration_mappings = configuration_mappings

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return "<Declaration: identifier = [%s], component_alias = [%s], config_mappings %s>" % \
               (self.identifier, self.component_alias, self.configuration_mappings)
