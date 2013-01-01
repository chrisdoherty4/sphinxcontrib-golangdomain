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
    r'''^([^(]*?)          # return type
        ([\w:.]+)  \s*     # thing name (colon allowed for C++)
        (?: \((.*)\) )?    # optionally arguments
        (\s+const)? $      # const specifier
    ''', re.VERBOSE)

go_func_sig_re = re.compile(
    r'''^(\s* func \s*)           # func
         (?: \((.*)\) )? \s*      # struct/interface name
         ([\w_.]+)                # thing name
         \( ([\w\s,]*) \) \s*     # arguments
         ([\w\s(),]*) \s* $       # optionally return type
    ''', re.VERBOSE)


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
    stopwords = set(('const', 'void', 'char', 'int', 'long', 'FILE', 'struct'))

    def _parse_type(self, node, ctype):
        # add cross-ref nodes for all words
        for part in filter(None, wsplit_re.split(ctype)):
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

    def handle_signature(self, sig, signode):
        """Transform a Go signature into RST nodes."""
        # first try the function pointer signature regex, it's more specific
        m = go_sig_re.match(sig)
        print "handle_signature:\nsig -> %s\n" % (sig,)

        if m is None:
            raise ValueError('no match')
        rettype, name, arglist, const = m.groups()
        print "handle_signature:\nrettype -> %s\nname->%s\narglist->%s\nconst->%s\n\n" % (rettype, name, arglist, const)

        signode += addnodes.desc_type('', '')
        self._parse_type(signode[-1], rettype)
        try:
            classname, funcname = name.split('::', 1)
            classname += '::'
            signode += addnodes.desc_addname(classname, classname)
            signode += addnodes.desc_name(funcname, funcname)
            # name (the full name) is still both parts
        except ValueError:
            signode += addnodes.desc_name(name, name)

        typename = self.env.temp_data.get('go:type')
        if self.name == 'go:member' and typename:
            fullname = typename + '.' + name
        else:
            fullname = name

        if not arglist:
            if self.objtype == 'function':
                # for functions, add an empty parameter list
                signode += addnodes.desc_parameterlist()
            if const:
                signode += addnodes.desc_addname(const, const)
            return fullname

        paramlist = addnodes.desc_parameterlist()
        arglist = arglist.replace('`', '').replace('\\ ', '') # remove markup
        # this messes up function pointer types, but not too badly ;)
        args = arglist.split(',')
        for arg in args:
            arg = arg.strip()
            param = addnodes.desc_parameter('', '', noemph=True)
            try:
                ctype, argname = arg.rsplit(' ', 1)
            except ValueError:
                # no argument name given, only the type
                self._parse_type(param, arg)
            else:
                self._parse_type(param, ctype)
                # separate by non-breaking space in the output
                param += nodes.emphasis(' '+argname, u'\xa0'+argname)
            paramlist += param
        signode += paramlist
        if const:
            signode += addnodes.desc_addname(const, const)
        return fullname

    def get_index_text(self, name):
        if self.objtype == 'function':
            return _('%s (Go function)') % name
        elif self.objtype == 'member':
            return _('%s (Go member)') % name
        elif self.objtype == 'macro':
            return _('%s (Go macro)') % name
        elif self.objtype == 'type':
            return _('%s (Go type)') % name
        elif self.objtype == 'const':
            return _('%s (Go const)') % name
        elif self.objtype == 'var':
            return _('%s (Go variable)') % name
        else:
            return ''

    def add_target_and_index(self, name, sig, signode):
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

        indextext = self.get_index_text(name)
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
        'member':   ObjType(l_('member'),   'member'),
        'macro':    ObjType(l_('macro'),    'macro'),
        'type':     ObjType(l_('type'),     'type'),
        'const':    ObjType(l_('const'),    'data'),
        'var':      ObjType(l_('variable'), 'data'),
    }

    directives = {
        'function': GoObject,
        'member':   GoObject,
        'macro':    GoObject,
        'type':     GoObject,
        'const':    GoObject,
        'var':      GoObject,
    }
    roles = {
        'func' :  GoXRefRole(fix_parens=True),
        'member': GoXRefRole(),
        'macro':  GoXRefRole(),
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
