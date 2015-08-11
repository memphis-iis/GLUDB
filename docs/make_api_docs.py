import pkgutil
from importlib import import_module
from functools import wraps
from inspect import (
    getmembers,
    isfunction,
    isclass,
    getdoc,
    formatargspec
)

# Support for Python 2 and 3 since we hope to eventually run this script
# with Python 3 when google's libs catch up to the rest of us
try:
    from inspect import getfullargspec
except:
    def getfullargspec(f):
        from inspect import getargspec
        return getargspec(f)

from qualname import qualname


def disp(s):
    return str(s).replace('_', '\_').replace('*', '\*')


class Outputter(object):
    def __init__(self):
        self.indent_level = 0
        self.indent_history = []

    def indent(self, inc):
        self.indent_level += inc
        self.output("")

    def push_indent(self):
        self.indent_history.append(self.indent_level)
        self.indent_level = 0

    def pop_indent(self):
        self.indent_level = self.indent_history.pop()

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


class IndentedBlock():
    def __enter__(self):
        indent()
        return self

    def __exit__(self, type, value, traceback):
        dedent()


def indented(func):
    @wraps(func)
    def wrapped(*args, **kwrds):
        with IndentedBlock():
            retval = func(*args, **kwrds)
        return retval
    return wrapped


def independent_indented(func):
    @wraps(func)
    def wrapped(*args, **kwrds):
        _outputter.push_indent()
        retval = func(*args, **kwrds)
        _outputter.pop_indent()
        return retval
    return wrapped


@independent_indented
@indented
def doc_package(package):
    header("Package %s", package.__name__)

    output(getdoc(package))

    for module_loader, name, ispkg in pkgutil.walk_packages(package.__path__):
        if ispkg:
            doc_package(import_module('.' + name, package.__name__))
        else:
            doc_module(package, import_module('.' + name, package.__name__))


@indented
def doc_module(package, mod):
    header("module %s", mod.__name__)

    output("(in pkg %s)", package.__name__)
    output("")
    output(getdoc(mod))

    for name, member in getmembers(mod):
        if name.startswith('_'):
            continue
        if isfunction(member):
            doc_function(mod, name, member)
        elif isclass(member):
            doc_class(mod, name, member)


@indented
def doc_function(mod, name, func):
    header("function *%s*", name)
    output(getdoc(func))


@indented
def doc_class(mod, name, cls):
    if cls.__module__ != mod.__name__:
        return

    header("class " + name)

    output("Full qualified name: %s.%s", mod.__name__, qualname(cls))
    output("")
    output(getdoc(cls))

    def skip(memname, member):
        return (
            not memname or
            not member or
            (memname.startswith('_') and memname != '__init__')
        )

    non_methods = []
    for memname, member in getmembers(cls):
        if skip(memname, member):
            pass  # Maybe log this one day?
        elif not isfunction(member):
            non_methods.append((memname, member))
        else:
            doc_member(mod, cls, memname, member)

    if non_methods:
        output("Class members that aren't methods")
        output("")
        for memname, member in sorted(non_methods):
            output(" + %s", disp(memname))


@indented
def doc_member(mod, cls, memname, member):
    header("method *%s*", disp(memname))

    args = getfullargspec(member)
    output('> Argument specification:')
    output('> ' + disp(formatargspec(*args)))
    output("")

    try:
        docstring = getdoc(member)
        docstring = docstring.strip() if docstring else ''
        if docstring == 'None':
            docstring = ''
    except:
        docstring = ''

    if docstring:
        output(docstring)


def main():
    doc_package(__import__("gludb"))

if __name__ == "__main__":
    main()
