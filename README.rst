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

    # tests/morelia.feature

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

    # tests/morelia_test.py

    class MoreliaTest(TestCase):
    
        def setUp(self):
            self.stack = []
    
        def step_I_have_entered_a_number_into_the_calculator(self, number):
            r'I have entered (\d+) into the calculator'
            self.stack.append(int(number))
    
        def step_I_press_add(self):  #  matched by method name
            self.result = sum(self.stack)
    
        def step_the_result_should_be_on_the_screen(self, number):
            "the result should be (\d+) on the screen"
            assert int(number) == self.result

        def test_evaluate_file(self):
            from morelia import Parser
            Parser().parse_file('tests/morelia.feature').evaluate(self)

And run it exactly the same as your regular tests. E.g.:

python -m unittest tests/morelia_test.py

Note that Morelia does not waste anyone's time inventing a new testing back-end
just to add a layer of literacy over our testage. Steps are miniature TestCases.
Your onsite customer need never know, and your unit tests and customer tests
can share their support methods. The same one test button can run all TDD and BDD tests.

Next, note that Morelia matches Steps in your Feature file to either the names
or doc-strings of *step_* methods in your test case.
And it expands regular expressions, such as `(\d+)`, into step arguments,
such as `number`.
Remember to use tight expressions, such as `(\d+)`,
not loosey-goose expressions like `(\d*)` or `(.*)`, to validate your input.

Documentation
=============

Full documentation is available at http://morelia.readthedocs.org/en/latest/index.html

.. image:: http://zeroplayer.com/images/stuff/sneakySnake.jpg
.. _the cheeseshop: http://pypi.python.org/pypi/Morelia/
.. _GitHub: http://github.com/kidosoft/Morelia/
