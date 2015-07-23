import pkgutil
# from inspect import getmro
from importlib import import_module

# TODO: actually create md files from docstrings
# TODO: run this under the make_docs.sh virtualenv

class Outputter(object):
    def __init__(self):
        self.indent_level = -1  # Just assume an initial indent

    def indent(self, inc):
        self.indent_level += inc

    def output(self, msg, *args):
        prefix = '    ' * self.indent_level if self.indent_level > 0 else ''
        if args:
            msg = msg % args
        print(prefix + msg)
_outputter = Outputter()
indent = lambda: _outputter.indent(1)
dedent = lambda: _outputter.indent(-1)
output = _outputter.output


def doc_module(package, mod):
    indent()
    output("Documenting module %s in pkg %s", mod.__name__, package.__name__)

    indent()
    for member in dir(mod):
        output(member)
    dedent()

    dedent()


def doc_package(package):
    indent()
    output("Documenting pkg %s", package.__name__)
    for module_loader, name, ispkg in pkgutil.walk_packages(package.__path__):
        if ispkg:
            doc_package(import_module('.' + name, package.__name__))
        else:
            doc_module(package, import_module('.' + name, package.__name__))
    dedent()


def main():
    doc_package(__import__("gludb"))

if __name__ == "__main__":
    main()
