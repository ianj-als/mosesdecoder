import glob
import os

from multimethod import multimethod, multimethodclass
from parser.import_spec import Import
from parser.component import Component
from parser.declaration import Declaration
from parser.expressions import Literal, \
     Identifier, \
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

    @staticmethod
    def __check_duplicate_names(stuff):
        dups = dict()
        returns = list()
        for identifier in stuff:
            if identifier.identifier in dups:
                returns.append(identifier)
            else:
                dups[identifier] = True

        return returns        

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
        duplicate_import_aliases = []

        if declarations:
            # Imported aliases
            import_aliases = [import_.alias for import_ in imports] if imports else []
            duplicate_import_aliases = ResolverVisitor.__check_duplicate_names(import_aliases)

            for decl in declarations:
                # Count occurrences of declaration identifiers
                try:
                    dups[decl] += 1
                except KeyError:
                    dups[decl] = 1

                # Ensure we have imported an alias that is being used
                # in this declaration
                if decl.component_alias not in import_aliases:
                    unknown_imports.append(decl.component_alias)

                # Ensure the 'from' end of a declaration mapping
                # exits in the configuration
                if decl.configuration_mappings:
                    for config_map in decl.configuration_mappings:
                        if isinstance(config_map.from_, Identifier):
                            if config_map.from_ in config:
                                config[config_map.from_] += 1
                            else:
                                missing_config.append(config_map.from_)

        unused_config = filter(lambda ce: config[ce] == 0, config)
        duplicate_declarations = filter(lambda de: dups[de] > 1, dups)

        return (tuple(missing_config),
                tuple(unused_config),
                tuple(unknown_imports),
                tuple(duplicate_declarations),
                tuple(duplicate_import_aliases))

    @staticmethod
    def __check_duplicate_declarations(declarations):
        pass

    @staticmethod
    def __add_messages(msg_fmt, collection, msg_collection):
        for entity in collection:
            info = {'entity' : entity,
                    'filename' : entity.filename,
                    'lineno' : entity.lineno}
            msg_collection.append(msg_fmt % info)

    def __add_errors(self, msg_fmt, collection):
        ResolverVisitor.__add_messages(msg_fmt, collection, self.__errors)

    def __add_warnings(self, msg_fmt, collection):
        ResolverVisitor.__add_messages(msg_fmt, collection, self.__warnings)

    def get_errors(self):
        return tuple(self.__errors)

    def get_warnings(self):
        return tuple(self.__warnings)

    @multimethod(Module)
    def visit(self, module):
        self.__current_module = module

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
            # Parse and resolve the module
            pcl_ast = parse_component(pcl_files[0])
            if pcl_ast:
                an_import.pcl_ast = pcl_ast
                pcl_resolver = ResolverVisitor(os.getenv("PCL_IMPORT_PATH", "."),
                                               os.getenv("PYTHONPATH", "."))
                an_import.pcl_ast.accept(pcl_resolver)
                pcl_warnings = pcl_resolver.get_warnings()
                for pcl_warning in pcl_warnings:
                    self.__warnings.append(pcl_warning)
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
            else:
                self.__errors.append("ERROR: %s at line %d, imported PCL module %s, with name %s, " \
                                     "failed to parse" % \
                                     (an_import.filename,
                                      an_import.lineno,
                                      pcl_files[0],
                                      an_import.module_name.identifier))
        elif not pcl_files and python_files:
            # Module is Python module
            an_import.python_file = python_files[0]
        elif pcl_files and python_files:
            self.__errors.append("ERROR: %s at line %d, module %s is duplicate" % \
                                 (an_import.filename,
                                  an_import.lineno,
                                  an_import.module_name.identifier))
        else:
            self.__errors.append("ERROR: %s at line %d, module %s not found" % \
                                 (an_import.filename,
                                  an_import.lineno,
                                  an_import.module_name.identifier))

        print "Import [%s] [%s]" % (an_import.module_name, an_import.alias)

    @multimethod(Component)
    def visit(self, component):
        print "Component [%s]" % (component)

        # Check for duplicates
        duplicate_inputs = ResolverVisitor.__check_duplicate_names(component.inputs)
        duplicate_outputs = ResolverVisitor.__check_duplicate_names(component.outputs)
        duplicate_config = ResolverVisitor.__check_duplicate_names(component.configuration)
        duplicate_decl_identifiers = ResolverVisitor.__check_duplicate_names(component.declarations)

        # Check that all the used configuration in declarations exist, and is used
        missing_configuration, \
        unused_configuration, \
        unknown_imports, \
        duplicate_declarations, \
        duplicate_import_aliases = ResolverVisitor.__check_declarations(component.configuration,
                                                                        component.declarations,
                                                                        component.module.imports)

        if duplicate_inputs or \
           duplicate_outputs or \
           duplicate_config or \
           duplicate_decl_identifiers or \
           missing_configuration or \
           unused_configuration or \
           unknown_imports or \
           duplicate_declarations or \
           duplicate_import_aliases:
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d input " \
                              "declaration contains duplicate identifier %(entity)s",
                              duplicate_inputs)
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d output " \
                              "declaration contains duplicate identifier %(entity)s",
                              duplicate_outputs)
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d configuration " \
                              "declaration contains duplicate identifier %(entity)s",
                              duplicate_config)
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d component " \
                              "declaration contains duplicate identifier %(entity)s",
                              duplicate_decl_identifiers)
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d component " \
                              "configuration does not exist %(entity)s",
                              missing_configuration)
            self.__add_warnings("WARNING: %(filename)s at line %(lineno)d component " \
                                "configuration is not used %(entity)s",
                                unused_configuration)
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d import not found " \
                              "in declaration %(entity)s",
                              unknown_imports)
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d duplicate declaration " \
                              "found %(entity)s",
                              duplicate_declarations)
            self.__add_errors("ERROR: %(filename)s at line %(lineno)d duplicate import alias " \
                              "found %(entity)s",
                              duplicate_import_aliases)

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

    @multimethod(IdentifierExpression)
    def visit(self, iden_expr):
        pass

    @multimethod(LiteralExpression)
    def visit(self, literal_expr):
        pass
