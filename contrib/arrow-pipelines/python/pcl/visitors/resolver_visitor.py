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
            if identifier in dups:
                returns.append(identifier)
            else:
                dups[identifier] = True

        return returns        

    @staticmethod
    def __check_duplicate_declarations(declarations):
        pass

    def __add_duplication_id_errors(self, msg_fmt, collection, **kwargs):
        for identifier in collection:
            kwargs['identifier'] = identifier
            self.__errors.append(msg_fmt % kwargs)

    def get_errors(self):
        return tuple(self.__errors)

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
                pcl_errors = pcl_resolver.get_errors()
                if pcl_errors:
                    self.__errors.append("ERROR: %s at line %d, imported PCL module %s, with name %s, is invalid" % \
                                         (an_import.filename,
                                          an_import.lineno,
                                          pcl_files[0],
                                          an_import.module_name.identifier))
                    for pcl_error in pcl_errors:
                        self.__errors.append(pcl_error)
            else:
                self.__errors.append("ERROR: %s at line %d, imported PCL module %s, with name %s, failed to parse" % \
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
        duplicate_inputs = ResolverVisitor.__check_duplicate_names(component.inputs.collection)
        duplicate_outputs = ResolverVisitor.__check_duplicate_names(component.outputs.collection)
        duplicate_config = ResolverVisitor.__check_duplicate_names(component.configuration.collection)
        duplicate_decl_identifiers = ResolverVisitor.__check_duplicate_names([decl.identifier
                                                                              for decl in component.declarations])

        # Check for duplicate declared identifiers
        duplicate_declarations = ResolverVisitor.__check_duplicate_declarations(component.declarations)

        if duplicate_inputs or \
           duplicate_outputs or \
           duplicate_config or \
           duplicate_decl_identifiers or \
           duplicate_declarations:
            self.__add_duplication_id_errors(self,
                                             "ERROR: %{filename}s at line %{lineno} input declaration contains duplicate identifier %{identifier}s",
                                             filename = component.inputs.filename,
                                             lineno = component.inputs.lineno)
            self.__add_duplication_id_errors(self,
                                             "ERROR: %{filename}s at line %{lineno} output declaration contains duplicate identifier %{identifier}s",
                                             filename = component.outputs.filename,
                                             lineno = component.outputs.lineno)
            self.__add_duplication_id_errors(self,
                                             "ERROR: %{filename}s at line %{lineno} configuration declaration contains duplicate identifier %{identifier}s",
                                             filename = component.configuration.filename,
                                             lineno = component.configuration.lineno)
            self.__add_duplication_id_errors(self,
                                             "ERROR: %{filename}s at line %{lineno} component declaration contains duplicate identifier %{identifier}s",
                                             filename = component.declarations.filename,
                                             lineno = component.declarations.lineno)

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
