.. acceptance test of golangdomain documentation master file, created by
   sphinx-quickstart on Mon Dec 31 17:50:00 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

acceptance test of golangdomain
===============================

Go language
-----------

Package 'foo'
~~~~~~~~~~~~~

.. go:package:: foo

.. go:const:: ConstTest

.. go:var:: VariableTest

.. go:type:: Spam

.. go:function:: func FuncOne()

.. go:function:: func FuncTwo(foo int)

.. go:function:: func FuncThree(spam string, egg uint)

.. go:function:: func FuncFour(spam, egg uint)

.. go:function:: func FuncFive() []string

.. go:function:: func FuncSix() (string, error)

.. go:function:: func FuncSeven() (string, int, error)

.. go:function:: func (Foo) MethodOne()

.. go:function:: func (Foo) MethodTwo(spam []int)

.. go:function:: func (Foo) MethodThree(spam string, egg uint)

.. go:function:: func (Foo) MethodFour(spam, egg uint)

.. go:function:: func (Foo) MothodFive() string

.. go:function:: func (Foo) MethodSix() (string, error)

.. go:function:: func (Foo) MethodSeven() (string, int, error)

.. go:function:: func (b Bar) MethodEight()


Test Case - Access without package name in the same package
-----------------------------------------------------------

:go:data:`ConstTest`

:go:data:`VariableTest`

:go:type:`Spam`

:go:func:`FuncOne`

:go:func:`(Foo) MethodOne`

:go:func:`(Bar) MethodEight`


.. go:package:: dummy_package

Test Case - Access with package name in other packages (dummy_package)
----------------------------------------------------------------------

.. go:type:: Spam

.. go:function:: func FuncOne()

:go:pkg:`foo`

:go:data:`foo.ConstTest`

:go:data:`foo.VariableTest`

:go:type:`foo.Spam`

:go:func:`foo.FuncOne`

:go:func:`(foo.Foo) MethodOne`

:go:func:`(foo.Bar) MethodEight`

following items should not be linked as current package is 'dummy_package'.

:go:type:`Spam`

:go:func:`FuncOne`


C language (for debug use)
--------------------------

.. c:var:: FooObject* FooClass_Type

.. c:type:: BarStruct

.. c:function:: int function_one(FooObject *foo)

.. c:function:: float function_two(FooObject foo, Bar_size_t size)


:c:type:`BarStruct`

:c:func:`function_one`



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

