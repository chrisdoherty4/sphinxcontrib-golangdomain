# -*- coding: utf-8 -*-
"""
    sphinx.domains.go
    ~~~~~~~~~~~~~~~~~

    The Go language domain.

    :copyright: Copyright 2012 by Yoshifumi YAMAGUCHI
    :license: BSD, see LICENSE for details.
"""

import re
import string

from docutils import nodes

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import Field, TypedField


# RE to split at word boundaries
wsplit_re = re.compile(r'(\W+)')

# REs for Go signatures
go_sig_re = re.compile(
    r'''^(\w+)                     # thing name
    ''', re.VERBOSE)

go_func_sig_re = re.compile(
    r'''^(\s* func \s*)            # func
         (?: \((.*)\) )? \s*       # struct/interface name
         ([\w_.]+)                 # thing name
         \( ([\w\s\[\],]*) \) \s*  # arguments
         ([\w\s\[\](),]*) \s* $    # optionally return type
    ''', re.VERBOSE)

go_method_re = re.compile(
    r'''^(\([\w\s()*]+\)) \s+      # struct name
         (\w+)                     # method name
    ''', re.VERBOSE)

def extract_method_name(name):
    m = go_method_re.match(name)
    if m is not None:
        print len(m.groups())
        _, method = m.groups()
    else:
        method = name
    return method


class GoObject(ObjectDescription):
    """
    Description of a Go language object.
    """

    doc_field_types = [
        TypedField('parameter', label=l_('Parameters'),
                   names=('param', 'parameter', 'arg', 'argument'),
                   typerolename='type', typenames=('type',)),
        Field('returnvalue', label=l_('Returns'), has_arg=False,
              names=('returns', 'return')),
        Field('returntype', label=l_('Return type'), has_arg=False,
              names=('rtype',)),
    ]

    # These Go types aren't described anywhere, so don't try to create
    # a cross-reference to them
    stopwords = set(('const', 'int', 'uint', 'uintptr', 'int8', 'int16', 
                     'int32', 'int64', 'uint8', 'uint16', 'uint32',
                     'uint64', 'string', 'error', '{}interface',
                     '..{}interface'))

    def _parse_type(self, node, gotype):
        # add cross-ref nodes for all words
        for part in filter(None, wsplit_re.split(gotype)):
            tnode = nodes.Text(part, part)
            if part[0] in string.ascii_letters+'_' and \
                   part not in self.stopwords:
                pnode = addnodes.pending_xref(
                    '', refdomain='go', reftype='type', reftarget=part,
                    modname=None, classname=None)
                pnode += tnode
                node += pnode
            else:
                node += tnode

    def _handle_general_signature(self, sig, signode, m):
        name, = m.groups()
        signode += addnodes.desc_name(name, name)
        fullname = name
        return fullname
    
    def _handle_func_signature(self, sig, signode, m):
        func, struct, name, arglist, rettype = m.groups()
        # debug
        print ("(struct, name, arglist, rettype) = ('%s', '%s', '%s', '%s')\n" 
               % (struct, name, arglist, rettype))

        if func:
            signode += addnodes.desc_addname("func", "func ")
        if struct:
            signode += addnodes.desc_addname("(", "(")
            signode += addnodes.desc_name("type", struct)
            signode += addnodes.desc_addname(") ", ") ")
            
        signode += addnodes.desc_name(name, name)
        if not arglist:
            signode += addnodes.desc_parameterlist()
        else:
            paramlist = addnodes.desc_parameterlist()
            args = arglist.split(",")
            for arg in args:
                arg = arg.strip()
                param = addnodes.desc_parameter('', '', noemph=True)
                try:
                    argname, gotype = arg.split(' ', 1)
                except ValueError:
                    # no argument name given, only the type
                    self._parse_type(param, arg)
                else:
                    param += nodes.emphasis(argname+' ', argname+u'\xa0')
                    self._parse_type(param, gotype)
                    # separate by non-breaking space in the output
                paramlist += param
            signode += paramlist

        if struct:
            fullname = "(%s) %s" % (struct, name)
        else:
            fullname = name
        return fullname

    def handle_signature(self, sig, signode):
        """Transform a Go signature into RST nodes."""
        # first try the function pointer signature regex, it's more specific
        print "handle_signature:\nsig -> %s" % (sig,)
        m = go_func_sig_re.match(sig)
        if m is not None:
            return self._handle_func_signature(sig, signode, m)
        else:
            m = go_sig_re.match(sig)
            return self._handle_general_signature(sig, signode, m)
        
    def get_index_text(self, name):
        if self.objtype == 'function':
            return _('%s (Go function)') % name
        elif self.objtype == 'type':
            return _('%s (Go type)') % name
        elif self.objtype == 'const':
            return _('%s (Go const)') % name
        elif self.objtype == 'var':
            return _('%s (Go variable)') % name
        else:
            return ''

    def add_target_and_index(self, name, sig, signode):
        # debug
        print ("add_target_and_index: (name, sig, signode) = (%s, %s, %s)\n" %
               (name, sig, signode))

        method = extract_method_name(name)
        # note target
        if name not in self.state.document.ids:
            signode['names'].append(name)
            signode['ids'].append(name)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            inv = self.env.domaindata['go']['objects']
            if name in inv:
                self.state_machine.reporter.warning(
                    'duplicate Go object description of %s, ' % name +
                    'other instance in ' + self.env.doc2path(inv[name][0]),
                    line=self.lineno)
            inv[name] = (self.env.docname, self.objtype)

        indextext = self.get_index_text(method)
        if indextext:
            self.indexnode['entries'].append(('single', indextext, name, ''))

    def before_content(self):
        self.typename_set = False
        if self.name == 'go:type':
            if self.names:
                self.env.temp_data['go:type'] = self.names[0]
                self.typename_set = True

    def after_content(self):
        if self.typename_set:
            self.env.temp_data['go:type'] = None


class GoXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        if not has_explicit_title:
            target = target.lstrip('~') # only has a meaning for the title
            # if the first character is a tilde, don't display the module/class
            # parts of the contents
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot+1:]
        return title, target


class GoDomain(Domain):
    """Go language domain."""
    name = 'go'
    label = 'Go'
    object_types = {
        'function': ObjType(l_('function'), 'func'),
        'type':     ObjType(l_('type'),     'type'),
        'const':    ObjType(l_('const'),    'data'),
        'var':      ObjType(l_('variable'), 'data'),
    }

    directives = {
        'function': GoObject,
        'type':     GoObject,
        'const':    GoObject,
        'var':      GoObject,
    }
    roles = {
        'func' :  GoXRefRole(fix_parens=True),
        'data':   GoXRefRole(),
        'type':   GoXRefRole(),
    }
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
    }

    def clear_doc(self, docname):
        for fullname, (fn, _) in self.data['objects'].items():
            if fn == docname:
                del self.data['objects'][fullname]

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        # strip pointer asterisk
        target = target.rstrip(' *')
        if target not in self.data['objects']:
            return None
        obj = self.data['objects'][target]
        return make_refnode(builder, fromdocname, obj[0], target,
                            contnode, target)

    def get_objects(self):
        for refname, (docname, type) in self.data['objects'].iteritems():
            yield (refname, refname, type, docname, refname, 1)


def setup(app):
    app.add_domain(GoDomain)
