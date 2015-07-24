import pkgutil
from importlib import import_module
from inspect import (
    getmembers,
    isfunction,
    isclass,
    getdoc,
    getfullargspec,
    formatargspec
)


class Outputter(object):
    def __init__(self):
        self.indent_level = 0

    def indent(self, inc):
        self.indent_level += inc
        self.output("")

    def output(self, msg, *args):
        if args:
            msg = msg % args
        print(msg)

    def header(self, msg, *args):
        if self.indent_level < 1:
            raise ValueError("indent level too low for header")
        prefix = '#' * self.indent_level
        self.output(prefix + ' ' + msg, *args)
        self.output("")

_outputter = Outputter()
indent = lambda: _outputter.indent(1)
dedent = lambda: _outputter.indent(-1)
header = _outputter.header
output = _outputter.output


def doc_package(package):
    indent()
    header("Package %s", package.__name__)

    output(getdoc(package))

    for module_loader, name, ispkg in pkgutil.walk_packages(package.__path__):
        if ispkg:
            doc_package(import_module('.' + name, package.__name__))
        else:
            doc_module(package, import_module('.' + name, package.__name__))
    dedent()


def doc_module(package, mod):
    indent()
    header("module %s (in pkg %s)", mod.__name__, package.__name__)

    output(getdoc(mod))

    for name, member in getmembers(mod):
        if name.startswith('_'):
            continue
        if isfunction(member):
            doc_function(mod, name, member)
        elif isclass(member):
            doc_class(mod, name, member)

    dedent()


def doc_function(mod, name, func):
    indent()
    header("function `%s`", name)
    output(getdoc(func))
    dedent()


def doc_class(mod, name, cls):
    if cls.__module__ != mod.__name__:
        return

    indent()
    header("class " + name)
    output(getdoc(cls))
    for memname, member in getmembers(cls):
        if memname.startswith('_') and memname != '__init__':
            continue

        indent()

        is_func = isfunction(member)
        header("%s `%s`", 'function ' if is_func else '', memname)

        if is_func:
            args = getfullargspec(member)
            output(' | ' + formatargspec(*args))

        docstring = ""
        try:
            docstring = getdoc(member)
            docstring = docstring.strip() if docstring else ''
        except:
            docstring = ""

        if docstring and docstring != 'None':
            output(docstring)

        dedent()

    dedent()


def main():
    doc_package(__import__("gludb"))

if __name__ == "__main__":
    main()
