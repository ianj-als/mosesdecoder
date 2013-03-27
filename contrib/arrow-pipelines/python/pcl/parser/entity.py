class Entity(object):
    def __init__(self, filename, lineno):
        self.filename = filename
        self.lineno = lineno

    def accept(self, visitor):
        visitor.visit(self)

    def __str__(self):
        return "<Entity: filename = [%s], line no = [%d]>" % \
               (self.filename, self.lineno)
