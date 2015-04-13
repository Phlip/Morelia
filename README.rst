#######
Morelia
#######

.. image:: https://pypip.in/wheel/Morelia/badge.svg
    :target: https://pypi.python.org/pypi/Morelia/
    :alt: Wheel Status

.. image:: https://pypip.in/version/Morelia/badge.svg
    :target: https://pypi.python.org/pypi/Morelia/
    :alt: Latest Version

.. image:: https://pypip.in/license/Morelia/badge.svg
    :target: https://pypi.python.org/pypi/Morelia/
    :alt: License

.. image:: https://travis-ci.org/kidosoft/Morelia.svg?branch=master
    :target: https://travis-ci.org/kidosoft/Morelia
    :alt: Build status

.. image:: https://coveralls.io/repos/kidosoft/Morelia/badge.svg
    :target: https://coveralls.io/r/kidosoft/Morelia
    :alt: Coverage

.. image:: https://readthedocs.org/projects/morelia/badge/?format=svg
    :target: https://morelia.readthedocs.org
    :alt: Documetation

Morelia *viridis* is a Python Behavior Driven Development platform, conceptually derived from Ruby's Cucumber Framework.

It is available both at `the cheeseshop`_ and GitHub_.

**Mascot**:

.. image:: http://www.naturfoto.cz/fotografie/ostatni/krajta-zelena-47784.jpg

Installation
============

    sudo pip install Morelia

Quick usage guide
=================

Write feature description:

.. code-block:: cucumber

    # calculator.feature

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    
    Scenario: Add two numbers
        Given I have entered 50 into the calculator
        And I have entered 70 into the calculator
        When I press add
        Then the result should be 120 on the screen


Create standard python's unittest and hook Morelia in it:

.. code-block:: python

    # test_acceptance.py

    import unittest
    from morelia import Parser

    class CalculatorTestCase(unittest.TestCase):
    
        def test_addition(self):
            Parser().parse_file('calculator.feature').evaluate(self)

Run test exaclty like your regular tests. Here's raw unittest example:

.. code-block:: console

   python -m unittest -v test_acceptance

And you'll see which steps are missing:

.. code-block:: python

    F
    ======================================================================
    FAIL: test_addition (__main__.CalculatorTestCase)
    Addition feature
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "test_acceptance.py", line 43, in test_addition
        Parser().parse_file('calculator.feature').evaluate(self)
      File "/.../morelia/base.py", line 184, in evaluate
        self.rip(step_matcher_visitor)
      File "/.../morelia/base.py", line 198, in rip
        visitor.after_feature(node)
      File "/.../morelia/visitors.py", line 117, in after_feature
        self._suite.fail(diagnostic)
    AssertionError: Cannot match steps:

        def step_I_have_powered_calculator_on(self):
            ur'I have powered calculator on'

            # code
            pass

        def step_I_have_entered_50_into_the_calculator(self):
            ur'I have entered 50 into the calculator'

            # code
            pass

        def step_I_have_entered_70_into_the_calculator(self):
            ur'I have entered 70 into the calculator'

            # code
            pass

        def step_I_press_add(self):
            ur'I press add'

            # code
            pass

        def step_the_result_should_be_120_on_the_screen(self):
            ur'the result should be 120 on the screen'

            # code
            pass


Now implement steps:

.. code-block:: python

    # test_acceptance.py

    import unittest
    from morelia import Parser
    
    class CalculatorTestCase(unittest.TestCase):
    
        def setUp(self):
            self.stack = []

        def test_addition(self):
            Parser().parse_file('calculator.feature').evaluate(self)
    
        def step_I_have_entered_a_number_into_the_calculator(self, number):
            ur'I have entered (\d+) into the calculator'  # match by regexp
            self.stack.append(int(number))
    
        def step_I_press_add(self):  #  matched by method name
            self.result = sum(self.stack)
    
        def step_the_result_should_be_on_the_screen(self, number):
            ur'the result should be {number} on the screen'  # match by format-like string
            assert int(number) == self.result

And run it again:

.. code-block:: console

    $ python -m unittest -v test_acceptance

    test_addition (test_acceptance.CalculatorTestCase)
    Addition feature ... ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.016s

    OK

Note that Morelia does not waste anyone's time inventing a new testing back-end
just to add a layer of literacy over our testage. Steps are miniature TestCases.
Your onsite customer need never know, and your unit tests and customer tests
can share their support methods. The same one test button can run all TDD and BDD tests.

Look at example directory for a little more enhanced example.

Documentation
=============

Full documentation is available at http://morelia.readthedocs.org/en/latest/index.html

.. image:: http://zeroplayer.com/images/stuff/sneakySnake.jpg
.. _the cheeseshop: http://pypi.python.org/pypi/Morelia/
.. _GitHub: http://github.com/kidosoft/Morelia/
