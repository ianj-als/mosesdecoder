import glob
import os

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
     IdentifierExpression, \
     LiteralExpression
from parser.mappings import Mapping, \
     TopMapping, \
     BottomMapping, \
     LiteralMapping
from parser.module import Module
from parser.helpers import parse_component


@multimethodclass
class ResolverVisitor(object):
    def __init__(self, pcl_import_path = [], python_import_path = []):
        if pcl_import_path:
            self.__pcl_import_paths = pcl_import_path.split(";")
        else:
            self.__pcl_import_paths = ["."]
        if python_import_path:
            self.__python_import_paths = python_import_path.split(";")
        else:
            self.__python_import_paths = ["."]
        self.__errors = []
        self.__warnings = []

    @staticmethod
    def __build_module_filename(identifier):
        split_identifier = identifier.identifier.split('.')
        if len(split_identifier) == 1:
            module_filename = split_identifier[0]
        else:
            module_filename = os.path.join(os.path.join(*split_identifier[:-1]),
                                           split_identifier[-1])

        return module_filename + ".[Pp][Cc][Ll]", module_filename + ".[Pp][Yy]"

    def __add_identifiers_to_symbol_table(self, identifiers, symbol_group_key):
        """Check for duplicate identifiers in a collection and add them
           to the module's symbol table. Return a tuple of duplicated
           identifiers."""
        symbol_dict = self.__module.resolution_symbols[symbol_group_key]
        returns = list()
        for identifier in identifiers:
            if identifier in symbol_dict:
                returns.append(identifier)
            symbol_dict[identifier] = identifier
        return tuple(returns)

    @staticmethod
    def __check_declarations(configuration, declarations, imports):
        # The configuration identifier to count map
        config = dict()
        if configuration:
            for c in configuration:
                config[c] = 0

        dups = dict()
        missing_config = []
        unknown_imports = []
        unknown_module_configuration = []
        python_module_interface = []

        if declarations:
            for decl in declarations:
                # Count occurrences of declaration identifiers
                try:
                    dups[decl] += 1
                except KeyError:
                    dups[decl] = 1

                # Lookup component alias in module symbol table
                try:
                    import_module_spec = imports[decl.component_alias]
                    if import_module_spec['type'] == 'pcl':
                        # Get the imported module configuration identifiers
                        import_module_config = import_module_spec['module'].definition.configuration
                        import_module_name = import_module_spec['module'].definition.identifier
                    else:
                        # Get the module inputs from the Python module's
                        # get_inputs() function
                        import_module_name = import_module_spec['module'].__name__
                        try:
                            import_module_config_fn = getattr(import_module_spec['module'],
                                                              'get_configuration')
                            # The Python module's component inputs
                            import_module_config = [Identifier(import_module_spec['module'].__name__, 0, c) \
                                                    for c in import_module_config_fn()]
                        except AttributeError:
                            python_module_interface.append({'module_name' : import_module_name,
                                                            'missing_function' : 'get_configuration'})
                            import_module_config = []
                except KeyError:
                    # Ensures we have imported an alias that is being used
                    # in this declaration
                    unknown_imports.append(decl.component_alias)
                
                # Ensure the 'from' end of a declaration mapping
                # exits in the configuration
                if decl.configuration_mappings:
                    for config_map in decl.configuration_mappings:
                        # Ensure we have the identifier configured
                        if isinstance(config_map.from_, Identifier):
                            if config_map.from_ in config:
                                config[config_map.from_] += 1
                            else:
                                missing_config.append(config_map.from_)

                        # Ensure that the module being used has the inputs
                        # we expect on construction
                        if config_map.to not in import_module_config:
                            unknown_module_configuration.append({'module_name' : import_module_name,
                                                                 'config_map' : config_map})

        unused_config = filter(lambda ce: config[ce] == 0, config)
        duplicate_declarations = filter(lambda de: dups[de] > 1, dups)

        return (tuple(missing_config),
                tuple(unused_config),
                tuple(unknown_imports),
                tuple(duplicate_declarations),
                tuple(unknown_module_configuration),
                tuple(python_module_interface))

    @staticmethod
    def __add_messages(msg_fmt, collection, unpack_fn, msg_collection):
        for entity in collection:
            info = unpack_fn(entity)
            msg_collection.append(msg_fmt % info)

    def __add_errors(self, msg_fmt, collection, unpack_fn):
        ResolverVisitor.__add_messages(msg_fmt, collection, unpack_fn, self.__errors)

    def __add_warnings(self, msg_fmt, collection, unpack_fn):
        ResolverVisitor.__add_messages(msg_fmt, collection, unpack_fn, self.__warnings)

    def has_errors(self):
        return len(self.__errors) > 0

    def get_errors(self):
        return tuple(self.__errors)

    def has_warnings(self):
        return len(self.__warnings) > 0

    def get_warnings(self):
        return tuple(self.__warnings)

    @multimethod(Module)
    def visit(self, module):
        self.__module = module
        self.__module.resolution_symbols = {'imports' : dict(),
                                            'components' : dict(),
                                            'inputs' : dict(),
                                            'outputs' : dict(),
                                            'configuration' : dict()}

    @multimethod(Import)
    def visit(self, an_import):
        pcl_filename, py_filename = ResolverVisitor.__build_module_filename(an_import.module_name)
        pcl_files = reduce(lambda x, y: x + y,
                           [glob.glob(os.path.join(directory, pcl_filename))
                            for directory in self.__pcl_import_paths])
        python_files = reduce(lambda x, y: x + y,
                              [glob.glob(os.path.join(directory, py_filename))
                               for directory in self.__python_import_paths])

        if pcl_files and not python_files:
            # Module is a PCL file
            # Parse the PCL module...
            pcl_ast = parse_component(pcl_files[0])
            if pcl_ast:
                # Resolve the PCL module...
                pcl_resolver = ResolverVisitor(os.getenv("PCL_IMPORT_PATH", "."),
                                               os.getenv("PYTHONPATH", "."))
                pcl_ast.accept(pcl_resolver)

                # Any warnings?
                pcl_warnings = pcl_resolver.get_warnings()
                for pcl_warning in pcl_warnings:
                    self.__warnings.append(pcl_warning)

                # Any errors?
                pcl_errors = pcl_resolver.get_errors()
                if pcl_errors:
                    self.__errors.append("ERROR: %s at line %d, imported PCL module %s, " \
                                         "with name %s, is invalid" % \
                                         (an_import.filename,
                                          an_import.lineno,
                                          pcl_files[0],
                                          an_import.module_name.identifier))
                    for pcl_error in pcl_errors:
                        self.__errors.append(pcl_error)

                # Add, only uniquely aliased, PCL modules to symbol table
                import_symbol_dict = an_import.module.resolution_symbols['imports']
                if import_symbol_dict.has_key(an_import.alias):
                    self.__errors.append("ERROR: %s at line %d, duplicate import alias found %s" % \
                                         (an_import.filename, an_import.lineno, an_import.alias))
                else:
                    import_symbol_dict[an_import.alias] = {'type' : 'pcl',
                                                           'module' : pcl_ast}
            else:
                self.__errors.append("ERROR: %s at line %d, imported PCL module %s, with name %s, " \
                                     "failed to parse" % \
                                     (an_import.filename,
                                      an_import.lineno,
                                      pcl_files[0],
                                      an_import.module_name.identifier))
        elif not pcl_files and python_files:
            # Module is Python module
            import_symbol_dict = an_import.module.resolution_symbols['imports']
            # Add, only uniquely aliased, Python modules to symbol table
            if import_symbol_dict.has_key(an_import.alias):
                self.__errors.append("ERROR: %s at line %d, duplicate import alias found %s" % \
                                     (an_import.filename, an_import.lineno, an_import.alias))
            else:
                print "Importing python %s" % an_import.module_name
                # Import the Python module
                import_symbol_dict[an_import.alias] = {'type' : 'python',
                                                       'module' : __import__(str(an_import.module_name),
                                                                             fromlist = ['get_configuration'])}
        elif pcl_files and python_files:
            self.__errors.append("ERROR: %s at line %d, ambiguous module import %s is both PCL and Python" % \
                                 (an_import.filename,
                                  an_import.lineno,
                                  an_import.module_name))
        else:
            self.__errors.append("ERROR: %s at line %d, module %s not found" % \
                                 (an_import.filename,
                                  an_import.lineno,
                                  an_import.module_name))

        print "Import [%s] [%s]" % (an_import.module_name, an_import.alias)

    @multimethod(Component)
    def visit(self, component):
        print "Component [%s]" % (component)

        # Add the inputs, outputs, configuration and declaration identifiers to
        # the module's symbol table
        duplicate_inputs = self.__add_identifiers_to_symbol_table(component.inputs, 'inputs')
        duplicate_outputs = self.__add_identifiers_to_symbol_table(component.outputs, 'outputs')
        duplicate_config = self.__add_identifiers_to_symbol_table(component.configuration, 'configuration')
        duplicate_decl_identifiers = self.__add_identifiers_to_symbol_table(component.declarations, 'components')

        # Check that all the used configuration in declarations exist, and is used
        missing_configuration, \
        unused_configuration, \
        unknown_imports, \
        duplicate_declarations, \
        unknown_module_configuration, \
        python_module_interace = ResolverVisitor.__check_declarations(component.configuration,
                                                                      component.declarations,
                                                                      component.module.resolution_symbols['imports'])
        if duplicate_inputs or \
           duplicate_outputs or \
           duplicate_config or \
           duplicate_decl_identifiers or \
           missing_configuration or \
           unused_configuration or \
           unknown_imports or \
           duplicate_declarations or \
           unknown_module_configuration or \
           python_module_interace:
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d input " \
                              "declaration contains duplicate identifier %(entity)s",
                              duplicate_inputs,
                              lambda e: {'entity' : e,
                                         'filename' : e.filename,
                                         'lineno' : e.lineno})
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d output " \
                              "declaration contains duplicate identifier %(entity)s",
                              duplicate_outputs,
                              lambda e: {'entity' : e,
                                         'filename' : e.filename,
                                         'lineno' : e.lineno})
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d configuration " \
                              "declaration contains duplicate identifier %(entity)s",
                              duplicate_config,
                              lambda e: {'entity' : e,
                                         'filename' : e.filename,
                                         'lineno' : e.lineno})
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d component " \
                              "declaration contains duplicate identifier %(entity)s",
                              duplicate_decl_identifiers,
                              lambda e: {'entity' : e,
                                         'filename' : e.filename,
                                         'lineno' : e.lineno})
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d component " \
                              "configuration does not exist %(entity)s",
                              missing_configuration,
                              lambda e: {'entity' : e,
                                         'filename' : e.filename,
                                         'lineno' : e.lineno})
            self.__add_warnings("WARNING: %(filename)s at line %(lineno)d component " \
                                "configuration is not used %(entity)s",
                                unused_configuration,
                                lambda e: {'entity' : e,
                                         'filename' : e.filename,
                                         'lineno' : e.lineno})
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d import not found " \
                              "in declaration %(entity)s",
                              unknown_imports,
                              lambda e: {'entity' : e,
                                         'filename' : e.filename,
                                         'lineno' : e.lineno})
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d duplicate declaration " \
                              "found %(entity)s",
                              duplicate_declarations,
                              lambda e: {'entity' : e,
                                         'filename' : e.filename,
                                         'lineno' : e.lineno})
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d configuration %(entity)s used which is not defined in module %(module_name)s",
                              unknown_module_configuration,
                              lambda e: {'entity' : e['config_map'].to,
                                         'module_name' : e['module_name'],
                                         'filename' : e['config_map'].filename,
                                         'lineno' : e['config_map'].lineno})
            self.__add_errors("ERROR: Python module %(module_name)s does not define mandatory function %(missing_function)s",
                              python_module_interace,
                              lambda e: e)

    @multimethod(Declaration)
    def visit(self, decl):
        pass

    @multimethod(UnaryExpression)
    def visit(self, unary_expr):
        pass

    @multimethod(CompositionExpression)
    def visit(self, comp_expr):
        pass

    @multimethod(ParallelWithTupleExpression)
    def visit(self, para_tuple_expr):
        pass

    @multimethod(ParallelWithScalarExpression)
    def visit(self, para_scalar_expr):
        pass

    @multimethod(FirstExpression)
    def visit(self, first_expr):
        pass

    @multimethod(SecondExpression)
    def visit(self, second_expr):
        pass

    @multimethod(SplitExpression)
    def visit(self, split_expr):
        pass

    @multimethod(MergeExpression)
    def visit(self, merge_expr):
        pass

    @multimethod(WireExpression)
    def visit(self, wire_expr):
        pass

    @multimethod(Mapping)
    def visit(self, mapping):
        pass

    @multimethod(TopMapping)
    def visit(self, mapping):
        pass

    @multimethod(BottomMapping)
    def visit(self, mapping):
        pass

    @multimethod(LiteralMapping)
    def visit(self, mapping):
        pass

    @multimethod(IdentifierExpression)
    def visit(self, iden_expr):
        pass

    @multimethod(LiteralExpression)
    def visit(self, literal_expr):
        pass
