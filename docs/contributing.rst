Contributing
============

This page will show the basic principals, that are used during the development of this package.

The project is `hosted`_ on the `github`_.

 .. _hosted: https://github.com/sergey-aganezov-jr/bg
 .. _github: https://github.com/

Test Driven Development
~~~~~~~~~~~~~~~~~~~~~~~
Whole project is written with a test-driven development paradigm.
This is especially important, since this project provides an implementation of a complex combinatorial object, which must be reliable in use during research projects.


Project uses `unittest framework`_ for implementing TDD paradigm.

.. _unittest framework: https://docs.python.org/3/library/unittest.html

Issues reporting
~~~~~~~~~~~~~~~~

Any found bugs, miss-citations, mistakes in documentation, questions, etc. shall be reported to the `issue-tracking`_
system, powered by github.

.. _issue-tracking: https://github.com/sergey-aganezov-jr/bg/issues

Code incorporation
~~~~~~~~~~~~~~~~~~
There are several rules for new code to be incorporated into this library:

1. All code has to written using the `Sphinx`_ style
2. All code must be covered by tests
3. All algorithms and data structures code must have proper citations

.. _Sphinx: https://pythonhosted.org/an_example_pypi_project/sphinx.html