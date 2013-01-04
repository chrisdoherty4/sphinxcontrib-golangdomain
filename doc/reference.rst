.. -*- coding: utf-8; restructuredtext -*-

Reference
=========

.. highlight:: rst

The Golang domain (name **go**) provides the following directives for module
declarations. Almost all directives are similar to Python's.

.. rst:directive:: .. go:package:: name

   This directive marks the beginning of the description of a package.

   This directive will also cause an entry in the global module index.


.. rst:directive:: .. go:currentpackage:: name

   .. seealso:: :rst:dir:`py:currentmodule`

The following directives are provided for global and module level contents:

.. rst:directive:: .. go:function:: name(signature) return

   Describes a function. Usage of this directive is almost as same as Python's one.
   
.. rst:directive:: .. go:const:: name

   Describes constant which starts with capital character.

The following directive is provided for module and class contents:

.. rst:directive:: .. go:function:: (type) name(signature) return

   Describes a struct method and a interface method. 
   Usage of this directive is almost as same as Python's one.
   
   .. seealso:: .. py:method:: name
                .. go:function:: name

The following directive is provided for module contents:

.. rst:directive:: .. go:type:: name

   Describes a struct.
   
      .. go:type:: Foo
         .. go:function:: quux() return

      -- or --

      .. go:type:: Bar

      .. go:function:: (Bar) quux() return

   The first way is the preferred one.



Info field lists
~~~~~~~~~~~~~~~~

Ruby domain has field lists as same as Python domain except ``key``, ``keyword``.

Cross-referencing Ruby objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following roles refer to objects in modules and are possibly hyperlinked if
a matching identifier is found:

.. rst:role:: go:pkg

   Reference a package

.. rst:role:: go:func

   Reference a Go function; a name with package may be used.
   The role text needs
   not include trailing parentheses to enhance readability; they will be added
   automatically by Sphinx if the :confval:`add_function_parentheses` config
   value is true (the default).
   
   If you want to refer package function, you should use following style::
   
      :go:func:`packagename.func_name`

.. rst:role:: go:const

   Reference a constant whose name starts with capital charactor.

.. rst:role:: go:meth

   Reference a method of an object.
   The role text can include the type name and
   the method name; if it occurs within the description of a type, 
   the type name can be omitted. 

   This role supports any kind of methods::
   
     :go:meth:`Struct.mehtod`
     :go:meth:`Interface.method`


