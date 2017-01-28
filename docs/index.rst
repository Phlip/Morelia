.. Morelia documentation master file, created by
   sphinx-quickstart on Fri Apr  3 18:27:12 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Morelia!
===================

Morelia is a Python Behavior Driven Development (BDD [#BDD]_) library.

BDD is an agile software development process that encourages
collaboration between developers, QA and business participants.

Test scenarios written in natural language make BDD foundation. They are comprehensible
for non-technical participants who wrote them yet unambiguous for developers and QA.

Morelia makes it easy for developers to integrate BDD into their existing unittest frameworks.
It is easy to run under nose, pytest, tox or integrate with django, flask or any other python framework
because no special code have to be written.

You as developer are in charge of how tests are organized. No need to fit into
rigid rules forced by some other BDD frameworks.

**Mascot**:

.. image:: http://www.naturfoto.cz/fotografie/ostatni/krajta-zelena-47784.jpg


If you're scenario writer (product owner/product manager/proffesional tester)
we recommended reading the:

* :ref:`writers-tutorial` and then
* :ref:`gherkin` when you need to create some more advanced scenarios

If you're programmer we recommended reading the:

* :ref:`usage-guide` and then
* :ref:`gherkin` and
* :ref:`api`

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   usage
   gherkin
   writers
   modules
   contributing
   authors
   history

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. rubric:: Footnotes

.. [#BDD] Behavior Driven Development https://en.wikipedia.org/wiki/Behavior-driven_development
