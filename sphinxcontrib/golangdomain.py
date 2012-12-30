# -*- coding: utf-8 -*-
"""
    sphinxcontrib.golangdomain
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Golang domain.

    :copyright: Copyright 2012 by Yohisufmi YAMAGUCHI
    :license: BSD, see LICENSE for details.

reference:
https://bitbucket.org/birkenfeld/sphinx-contrib/src/f4826e5bcff8/erlangdomain/sphinxcontrib/erlangdomain.py?at=default
"""

import re
import string

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType, Index
from sphinx.util.compat import Directive
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import Field, TypedField


# TODO(ymotongpoo): implement golang func pattern
go_func_sig_re = re.compile(r'''
^([\w.]*\.)?     # package name
 (\w+)\(         # func name
 (?:)
''',re.VERBOSE)


class GolangObject(ObjectDescription):
    """
    Description of a Golang language object.
    """
    pass


class GolangDomain(Domain):
    """Go programming language domain."""
    name = 'go'
    label = 'golang'
    object_types = {
        'function':  ObjType(l_('function'), 'func'),
        'package':   ObjType(l_('package'), 'package'),
        'struct':    ObjType(l_('struct'), 'struct'),
        'interface': ObjType(l_('interface'), 'interface'),
        }

    directives = {
        'function':       GolangObject,
        'package':        GolangObject,
        'struct':         GolangObject,
        'interface':      GolangPackage,
        'currentpackage': GolangPackage,
        }

    roles = {
        'func':      GolangXRefRole(),
        'package':   GolangXRefRole(),
        'struct':    GolangXRefRole(),
        'interface': GolangXRefRole(),
        }

    initial_data = {
        'objects': {},
        'functions': {},
        'packages': {},
        }


def setup(app):
    app.add_domain(GolangDomain)
