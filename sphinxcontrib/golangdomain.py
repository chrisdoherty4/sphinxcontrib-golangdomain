# -*- coding: utf-8 -*-
"""
    sphinx.domains.golang
    ~~~~~~~~~~~~~~~~~~~~~

    The Go language domain.

    :copyright: Copyright 2012 by Yoshifumi YAMAGUCHI
    :license: BSD, see LICENSE for details.
"""

import re
import string

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.util.compat import Directive
from sphinx.util.docfields import Field, TypedField


# RE to split at word boundaries
wsplit_re = re.compile(r'(\W+)')

# REs for Go signatures
go_sig_re = re.compile(
    r'''^([\w.]*\.)?       # package name
        ([\w:.]+)  \s*     # thing name
        (?:\((.*)\)        # optional: arguments
         (?:\s \s* (.*))?  #           return annotation
        )? $               # and nothing more
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
    stopwords = set(('const', 'nil', 'uint', 'uint8', 'uint16', 'uint32', 
                     'uint64', 'int', 'int8', 'int16', 'int32', 'int64', 
                     'float32', 'float64', 'complex64', 'complex128', 
                     'byte', 'rune', 'uintptr', 'string'))

    def _parse_type(self, node, gotype):
        print "_parse_type: %s, %s, %s\n" % (node, type(gotype), gotype)
        # add cross-ref nodes for all words
        if gotype:
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

    def handle_signature(self, sig, signode):
        """Transform a Go signature into RST nodes."""
        m = go_sig_re.match(sig)
        if m is None:
            raise ValueError('no match')
        name_prefix, name, arglist, rettype = m.groups()

        pkgname = self.options.get(
            'package', self.env.temp_data.get('go:package'))
        if name_prefix:
            fullname = name_prefix + name
        else:
            fullname = name

        signode['package'] = pkgname
        signode['fullname'] = fullname
       
        signode += addnodes.desc_type('', '')
        if name_prefix:
            signode += addnodes.desc_addname(name_prefix, name_prefix)

        self._parse_type(signode[-1], rettype)

        if not arglist:
            if self.objtype == 'function':
                # for functions, add an empty parameter list
                signode += addnodes.desc_parameterlist()
            return fullname

        paramlist = addnodes.desc_parameterlist()
        arglist = arglist.replace('`', '').replace('\\ ', '') # remove markup
        # this messes up function pointer types, but not too badly ;)
        args = arglist.split(',')
        for arg in args:
            arg = arg.strip()
            param = addnodes.desc_parameter('', '', noemph=True)
            try:
                argname, gotype = arg.rsplit(' ', 1)
            except ValueError:
                # no argument name given, only the type
                self._parse_type(param, arg)
            else:
                self._parse_type(param, gotype)
                # separate by non-breaking space in the output
                param += nodes.emphasis(' '+argname, u'\xa0'+argname)
            paramlist += param
        signode += paramlist
        return fullname

    def get_index_text(self, pkgname, name):
        if pkgname:
            fullname = pkgname + '.' + name
        else:
            fullname = name

        if self.objtype == 'function':
            return _('%s (Go function)') % fullname
        elif self.objtype == 'type':
            return _('%s (Go type)') % fullname
        elif self.objtype == 'const':
            return _('%s (Go const)') % fullname
        elif self.objtype == 'var':
            return _('%s (Go variable)') % fullname
        elif self.objtype == 'package':
            return _('%s (Go package)') % fullname
        else:
            return ''

    def add_target_and_index(self, name, sig, signode):
        pkgname = self.options.get(
            'package', self.env.temp_data.get('go:package'))
        fullname = (pkgname and pkgname + "." or '') + name[0]

        # note target
        if fullname not in self.state.document.ids:
            signode['names'].append(fullname)
            signode['ids'].append(fullname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            objects = self.env.domaindata['go']['objects']
            if fullname in objects:
                self.state_machine.reporter.warning(
                    'duplicate Go object description of %s, ' % fullname +
                    'other instance in ' + self.env.doc2path(objects[fullname][0]),
                    line=self.lineno)
            objects[name] = (self.env.docname, self.objtype)

        indextext = self.get_index_text(pkgname, name)
        if indextext:
            self.indexnode['entries'].append(('single', indextext,
                                              fullname, ''))

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
        refnode["go:package"] = env.temp_data.get("go:package")
        if not has_explicit_title:
            title = title.lstrip('.')
            target = target.lstrip('~') # only has a meaning for the title
            # if the first character is a tilde, don't display the module/class
            # parts of the contents
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot+1:]

        if target[0:1] == '.':
            target = target[1:]
            refnode['refspecific'] = True
        return title, target


class GoPackage(Directive):
    """
    Directive to mark description of a new package.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'platform': lambda x: x,
        'synopsis': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        pkgname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['go:package'] = pkgname
        env.domaindata['go']['packages'][pkgname] = \
            (env.docname, self.options.get('synopsis', ''),
             self.options.get('platform', ''), 'deprecated' in self.options)
        targetnode = nodes.target('', '', ids=['package-' + pkgname], ismod=True)
        self.state.document.note_explicit_target(targetnode)
        ret = [targetnode]
        # XXX this behavior of the module directive is a mess...
        if 'platform' in self.options:
            platform = self.options['platform']
            node = nodes.paragraph()
            node += nodes.emphasis('', _('Platforms: '))
            node += nodes.Text(platform, platform)
            ret.append(node)
        # the synopsis isn't printed; in fact, it is only used in the
        # modindex currently
        if not noindex:
            indextext = _('%s (package)') % pkgname
            inode = addnodes.index(entries=[('single', indextext,
                                             'package-' + pkgname, pkgname)])
            ret.append(inode)
        return ret


class GoPackageIndex(Index):
    """
    Index subclass to provide the Go module index.
    """

    name = 'pkgindex'
    localname = l_('Go Package Index')
    shortname = l_('packages')

    def generate(self, docnames=None):
        content = {}
        # list of prefixes to ignore
        ignores = self.domain.env.config['modindex_common_prefix']
        ignores = sorted(ignores, key=len, reverse=True)
        # list of all modules, sorted by module name
        packages = sorted(self.domain.data['packages'].iteritems(),
                          key=lambda x: x[0].lower())
        # sort out collapsable modules
        prev_pkgname = ''
        num_toplevels = 0
        for pkgname, (docname, synopsis, platforms, deprecated) in packages:
            if docnames and docname not in docnames:
                continue

            for ignore in ignores:
                if pkgname.startswith(ignore):
                    pkgname = pkgname[len(ignore):]
                    stripped = ignore
                    break
            else:
                stripped = ''

            # we stripped the whole module name?
            if not pkgname:
                pkgname, stripped = stripped, ''

            entries = content.setdefault(pkgname[0].lower(), [])

            package = pkgname.split('::')[0]
            if package != pkgname:
                # it's a subpackage
                if prev_pkgname == package:
                    # first submodule - make parent a group head
                    entries[-1][1] = 1
                elif not prev_pkgname.startswith(package):
                    # submodule without parent in list, add dummy entry
                    entries.append([stripped + package, 1, '', '', '', '', ''])
                subtype = 2
            else:
                num_toplevels += 1
                subtype = 0

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([stripped + pkgname, subtype, docname,
                            'package-' + stripped + pkgname, platforms,
                            qualifier, synopsis])
            prev_pkgname = pkgname

        # apply heuristics when to collapse pkgindex at page load:
        # only collapse if number of toplevel package is larger than
        # number of submodules
        collapse = len(packages) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse


class GoDomain(Domain):
    """Go language domain."""
    name = 'go'
    label = 'Go'
    object_types = {
        'function': ObjType(l_('function'), 'func', 'obj'),
        'type':     ObjType(l_('type'),     'type', 'obj'),
        'var':      ObjType(l_('variable'), 'data', 'obj'),
        'const':    ObjType(l_('const'),    'data', 'obj'),
        'package':  ObjType(l_('package'),  'pkg', 'obj')

    }
    directives = {
        'function': GoObject,
        'type':     GoObject,
        'var':      GoObject,
        'const':    GoObject,
        'package':  GoPackage,
    }
    roles = {
        'func' :  GoXRefRole(fix_parens=True),
        'data':   GoXRefRole(),
        'type':   GoXRefRole(),
        'obj':    GoXRefRole(),
    }
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
        'packages': {},
    }
    indecies = [
        GoPackageIndex,
        ]

    def clear_doc(self, docname):
        for fullname, (fn, _) in self.data['objects'].items():
            if fn == docname:
                del self.data['objects'][fullname]
        for pkgname, (fn, _, _, _) in self.data['packages'].items():
            if fn == docname:
                del self.data['packages'][pkgname]

    def find_obj(self, env, pkgname, name, typ, searchorder=0):
        # skip parens
        if name[-2:] == '()':
            name = name[:-2]

        if not name:
            return None, None
        
        objects = self.data['objects']

        newname = None
        if name in objects:
            newname = name
        elif pkgname and pkgname + '.' + name in objects:
            newname = pkgname + '.' + name
        elif name in objects:
            newname = name

        if newname is None:
            return None, None

        return newname, objects[newname]

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        # strip pointer asterisk and reference ampersand
        target = target.lstrip(' *&')
        if (typ == 'pkg' or
            typ == 'obj' and target in self.data['packages']):
            docname, synopsis, platform, deprecated = \
                self.data['packages'].get(target, ('','','',''))
            if not docname:
                return None
            else:
                title = '%s%s%s' % ((platform and '(%s) ' % platform),
                                    synopsis,
                                    (deprecated and ' (deprecated)' or ''))
                return make_refnode(builder, fromdocname, docname,
                                    'package-'+target, contnode, title)
        else:
            pkgname = node.get('go:package')
            name, obj = self.find_obj(env, pkgname, target, typ)
            print 'resolve_xref: %s\n' % name
            return make_refnode(builder, fromdocname, obj[0], target,
                                    contnode, target)

    def get_objects(self):
        for pkgname, info in self.data['packages'].iteritems():
            yield (pkgname, pkgname, 'package', info[0], 'package-'+pkgname, 0)
        for refname, (docname, type) in self.data['objects'].iteritems():
            yield (refname, refname, type, docname, refname, 1)


def setup(app):
    app.add_domain(GoDomain)
