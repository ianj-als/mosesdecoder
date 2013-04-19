import os
import sys

from parser.helpers import parse_component
from visitors.resolver_visitor import ResolverVisitor
from visitors.executor_visitor import ExecutorVisitor


if __name__ == '__main__':
    ast = parse_component(sys.argv[1])
    print ast

    pcl_import_path = os.getenv("PCL_IMPORT_PATH", ".")
    python_import_path = os.getenv("PYTHONPATH", ".")
    resolver = ResolverVisitor(pcl_import_path, python_import_path)
    ast.accept(resolver)
    errors = resolver.get_errors()
    if errors:
        for error in errors:
            print error
    else:
        executor = ExecutorVisitor()
        ast.accept(executor)
