"""
Copyright (C) 2013 Sioux Embedded Systems

Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or 
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING B
UT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
Script to generate enhanced enums and associated string conversion operators in C++. This code 
is very tedious and repetitive to write, hence this generator.
"""

from os import path
from StringIO import StringIO

defined_enums = []

class Enum:
    def __init__(self, module, name, optionlist):
        self.module     = module
        self.name       = name
        self.optionlist = optionlist

    def namespaces(self):
        """
        Return all namespaces in the type definition (including the enum name itself, as we're going to use it as a namespace0

        >>> Enum('', 'A::B::C', {}).namespaces()
        ['A', 'B', 'C']
        """
        return self.name.split('::')

    def fulltypename(self):
        """
        Return tye type's full name
        """
        return self.name

    def typename(self):
        """
        Return the type's simple name

        >>> Enum('', 'A::B::C', {}).typename()
        'C'
        """
        return self.name.split('::')[-1]

    def basename(self):
        """
        Return the basename of the generated files

        >>> Enum('foo', 'A::B::C', {}).basename().replace('\\\\', '/')
        'foo/c'
        >>> Enum('', 'A::B::C', {}).basename()
        'c'
        """
        return path.join(self.module, self.typename().lower())

    def symbolic_names(self):
        return [x[0] for x in self.optionlist]

    def option_mapping(self):
        return ((key, (value if value != None else key)) for key, value in self.optionlist)


def define(module, name, optionlist):
    """
    Define the given enum at the given location with the given symbolic names
    and descriptive strings

    - module: a module/directory specification to put the generated files in.
    - name: a namespace::type name to name the enum. The filename will be based
      on this name.
    - optionlist: a mapping of (SYMBOLIC_NAME, DESCRIPTIVE_TEXT) to use for the
      enum. You can use None as the descriptive text, in which case the symbolic
      name will be used.
    """
    global defined_enums
    defined_enums.append(Enum(module, name, optionlist))

def transpose(d):
    """
    Transpose a dictionary

    >>> transpose({1: 2})
    {2: 1}
    """
    return dict((v, k) for k, v in d.items())

def header_writer(modelfile):
    def _(output):
        output.write("""
/**
 ********************************************************************
 *
 * WARNING! This file was automatically generated. Do not edit it, as your
 * changes will be lost. Edit %s instead.
 *
 ********************************************************************
 */

""" % modelfile)
    return _

def define_guard_writer(define_guard, writer):
    def _(output):
        output.write("#ifndef %(define_guard)s\n#define %(define_guard)s\n" % { 'define_guard' : define_guard })

        invoke(output, writer)

        output.write("#endif // %s\n" % define_guard)
    return _

def namespace_writer(namespaces, writer):
    def _(output):
        # Open namespaces
        for ns in namespaces:
            output.write("namespace %s\n{\n" % ns)

        invoke(output, writer)

        # Close namespaces
        for ns in namespaces:
            output.write("}\n")
    return _

def enum_writer(body):
    def _(output):
        output.write("enum Enum\n{\n")
        invoke(output, body)
        output.write("};\n")
    return _

def options_writer(options):
    return lambda output : output.write(''.join(["    %s,\n" % name for name in options]) + '    _Count\n')

def line_writer(*lines):
    def _(output):
        for line in lines: output.write(line + '\n')
    return _

def fn_decl_writer(decl, body):
    """
    Write the given function declaration, and optionally a body
    """
    def _(output):
        output.write(decl)
        if body:
            output.write('\n{\n')
            invoke(output, body)
            output.write('}\n')
        else:
            output.write(';\n')
    return _

def stream_op_writer(typename, body):
    """
    Write the stream operator function declaration, optionally with the given body
    """
    return fn_decl_writer('std::ostream& operator<<(std::ostream& os, const %(typename)s::Enum& e)' % { 'typename': typename }, body)

def switch_writer(body):
    def _(output):
        output.write("    switch (e)\n")
        output.write("    {\n")

        invoke(output, body)

        output.write('        default : return os << "???"; \n')
        output.write("    }\n")
    return _


def values_fn_decl_writer(body):
    """
    Write the values() function declaration, optionally with the given body
    """
    return fn_decl_writer('std::vector<Enum> values()', body)

def values_fn_body_writer(values):
    """
    Write the values() function body
    """
    def _(output):
        output.write('    static std::vector<Enum> v;\n')
        output.write('    if (!v.size())\n')
        output.write('    {\n')
        for v in values:
            output.write('        v.push_back(%s);\n' % v)
        output.write('    }\n')
        output.write('    return v;\n')
    return _

def valueof_fn_decl_writer(body):
    """
    Write the valueOf() function declaration
    """
    return fn_decl_writer('Enum valueOf(std::string str)', body)

def valueof_fn_body_writer(names):
    """
    Write the valueOf() mapping body
    """
    def _(output):
        for n in names:
            output.write('    if (str == "%s") return %s;\n' % (n, n))
        output.write('    return (Enum)0;\n')
    return _

def name_fn_decl_writer(body):
    """
    Write the name() function declaration
    """
    return fn_decl_writer('std::string name(Enum e)', body)

def name_fn_body_writer(names):
    """
    Write the name() mapping body
    """
    def _(output):
        output.write("    switch (e)\n")
        output.write("    {\n")
        for n in names:
            output.write('        case %s: return "%s";\n' % (n, n))
        output.write('        default : return "???";\n')
        output.write("    }\n")
    return _


def cases_writer(case_tuples, prefix=''):
    def _(output):
        for key, value in case_tuples:
            output.write('        case %s : return os << "%s";\n' % (prefix + key, value))
    return _

def invoke(output, writer):
    if writer:
        if callable(writer):
            writer(output)
        else:
            for w in writer:
                w(output)

def write_h_file(enum, modelfile, output):
    define_guard = enum.typename().upper() + '_H'
    invoke(output, [
        header_writer(modelfile),
        define_guard_writer(define_guard, [
            line_writer('#include <ostream>', '#include <vector>', '#include <string>'),
            namespace_writer(enum.namespaces(), [
                enum_writer(
                    options_writer(enum.symbolic_names())),
                values_fn_decl_writer(None),
                name_fn_decl_writer(None),
                valueof_fn_decl_writer(None)
            ]),

            # We need the stream operator to be outside any namespace as the string_of function
            # it's going to be used by is also not in any namespace.
            stream_op_writer(enum.fulltypename(), None)
        ])
    ])

def write_cpp_file(enum, h_file, modelfile, output):
    invoke(output, [
        header_writer(modelfile),
        line_writer('#include "%s"' % h_file),
        namespace_writer(enum.namespaces(), [
            values_fn_decl_writer(values_fn_body_writer(enum.symbolic_names())),
            name_fn_decl_writer(name_fn_body_writer(enum.symbolic_names())),
            valueof_fn_decl_writer(valueof_fn_body_writer(enum.symbolic_names()))
        ]),
        stream_op_writer(enum.fulltypename(), 
            switch_writer(
                cases_writer(enum.option_mapping(), enum.fulltypename() + '::')
        ))
    ])

def invoke_file_writer(filename, writer, args):
    """
    Invoke the given file writer function with the given arguments and a
    file-like object as an additional (last) parameter
    
    Replace the target file with whatever the file writer produced, but ONLY if 
    the file has changed (to prevent unnecessarily updating the file time stamp
    leading to rebuilds).
    """
    out = StringIO()
    writer_args = args + (out, ) # Concatenate outfile to arguments
    writer(*writer_args)

    current_contents = file(filename, 'r').read() if path.isfile(filename) else ''
    if current_contents != out.getvalue():
        print path.realpath(filename)
        file(filename, 'w').write(out.getvalue())

def write(root_path, modelfile):
    """
    Write all files to the subpath
    """
    global defined_enums
    for enum in defined_enums:
        base = path.join(root_path, enum.basename())

        h_file   = base + '.h'
        cpp_file = base + '.cpp'

        invoke_file_writer(h_file,   write_h_file,   (enum, modelfile))
        invoke_file_writer(cpp_file, write_cpp_file, (enum, path.basename(h_file), modelfile))

if __name__ == '__main__':
    import doctest
    doctest.testmod()

