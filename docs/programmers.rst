For programmers
===============

Matching steps
--------------

Methods from test case object are matched with:

* `Regular expressions`_
* `Format-like strings`_
* `Method names`_


If you look in example from :ref:`usage-guide`:

.. code-block:: python

    # test_acceptance.py

    import unittest

    from morelia import run


    class CalculatorTestCase(unittest.TestCase):
    
        def test_addition(self):
            """ Addition feature """
            filename = os.path.join(os.path.dirname(__file__), 'calculator.feature')
            run(filename, self, verbose=True, show_all_missing=True)
    
        def step_I_have_powered_calculator_on(self):
            r'I have powered calculator on'
            self.stack = []

        def step_I_enter_a_number_into_the_calculator(self, number):
            r'I enter "(\d+)" into the calculator'  # match by regexp
            self.stack.append(int(number))
    
        def step_I_press_add(self):  #  matched by method name
            self.result = sum(self.stack)
    
        def step_the_result_should_be_on_the_screen(self, number):
            r'the result should be "{number}" on the screen'  # match by format-like string
            self.assertEqual(int(number), self.result)
    
You'll see three types of matching.

Regular expressions
^^^^^^^^^^^^^^^^^^^

Method ``step_I_enter_number_into_the_calculator`` from example is matched
by :py:mod:`regular expression <re>` as it's docstring

.. code-block:: python

        r'I enter "(\d+)" into the calculator'

matches steps:

.. code-block:: cucumber

        When I enter "50" into the calculator
        And I enter "70" into the calculator

Regular expressions, such as ``(\d+)``, are expanded into positional step arguments,
such as ``number`` in above example. If you would use named groups like ``(?P<number>\d+)``
then capttured expressions from steps will be put as given keyword argument to method.

Remember to use tight expressions, such as ``(\d+)``,
not expressions like ``(\d*)`` or ``(.*)``, to validate your input.

Format-like strings
^^^^^^^^^^^^^^^^^^^

Method ``step_the_result_should_be_on_the_screen`` from example is matched
by :py:class:`format-like strings <string.Formatter>` as it's docstring

.. code-block:: python

        r'the result should be "{number}" on the screen'

matches step:

.. code-block:: cucumber

        Then the result should be "120" on the screen

Method names
^^^^^^^^^^^^

Method ``step_I_press_add`` from example is matched by method name which matches
step:

.. code-block:: cucumber

        And I press add

Own matchers
^^^^^^^^^^^^

You can limit matchers for only some types or use your own matchers.
Matcher classes can be passed to :py:func:`morelia.run` method as keyword parameter:

.. code-block:: python

   from morelia.matchers import RegexpStepMatcher
   # ...
   run(filename, self, matchers=[MyOwnMatcher, RegexpStepMatcher])


See api for :py:meth:`morelia.matchers.IStepMatcher`.


Tables
^^^^^^

If you use Scenarios with tables and `<angles>` around the payload variable names:

.. code-block:: cucumber

    Scenario: orders above $100.00 to the continental US get free ground shipping
      When we send an order totaling $<total>, with a 12345 SKU, to our warehouse
       And the order will ship to <destination>
      Then the ground shipping cost is $<cost>
       And <rapid> delivery might be available
    
           |  total | destination            |  cost | rapid |
    
           |  98.00 | Rhode Island           |  8.25 |  yes  |
           | 101.00 | Rhode Island           |  0.00 |  yes  |
           |  99.00 | Kansas                 |  8.25 |  yes  |
           | 101.00 | Kansas                 |  0.00 |  yes  |
           |  99.00 | Hawaii                 |  8.25 |  yes  |
           | 101.00 | Hawaii                 |  8.25 |  yes  |
           | 101.00 | Alaska                 |  8.25 |  yes  |
           |  99.00 | Ontario, Canada        | 40.00 |   no  |
           |  99.00 | Brisbane, Australia    | 55.00 |   no  |
           |  99.00 | London, United Kingdom | 55.00 |   no  |
           |  99.00 | Kuantan, Malaysia      | 55.00 |   no  |
           | 101.00 | Tierra del Fuego       | 55.00 |   no  |

then that Scenario will unroll into a series of scenarios,
each with one value from the table inserted into their placeholders `<total>`,
`<destination>`, and `<rapid>`.
So this step method will receive each line in the "destination" column:

.. code-block:: python

    def step_the_order_will_ship_to_(self, location):
        r'the order will ship to (.*)'

(And observe that naming the placeholder the same as the method argument
is a *reeeally* good idea, but naturally unenforceable.)

Morelia will take each line of the table,
and construct a complete test case out of the Scenario steps,
running :py:meth:`unittest.TestCase.setUp()` and :py:meth:`unittest.TestCase.tearDown()` around them.

If you use many tables then Morelia would use permutation of all rows in all tables:

.. code-block:: cucumber

    Scenario: orders above $100.00 to the continental US get free ground shipping
      When we send an order totaling $<total>, with a 12345 SKU, to our warehouse
       And the order will ship to <destination>
       And we choose that delivery should be <speed>
            | speed   |

            | rapid   |
            | regular |

      Then the ground shipping cost is $<cost>
    
           |  total | destination            |  cost | 
    
           |  98.00 | Rhode Island           |  8.25 | 
           | 101.00 | Rhode Island           |  0.00 | 
           |  99.00 | Kansas                 |  8.25 | 

In above example 2 * 3 = 6 different test cases would be generated.


Formatters
----------

Morelia complies with Unix's `Rule of Silence` [#ROS]_ so when you hook it like this:

.. code-block:: python

    run(filename, self)

and all tests passes it would say nothing:

.. code-block:: console

    $ python -m unittest test_acceptance
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.028s

    OK

(here's only information from test runner)

But when something went wrong it would complie with Unix's `Rule of Repair` [#ROR]_
and fail noisily:

.. code-block:: console

    F
    ======================================================================
    FAIL: test_addition (test_acceptance.CalculatorTestCase)
    Addition feature
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "test_acceptance.py", line 45, in test_addition
        run(filename, self, show_all_missing=True)
      File "(..)/morelia/__init__.py", line 22, in run
        return ast.evaluate(suite, **kwargs)
      File "(...)/morelia/grammar.py", line 36, in evaluate
        feature.evaluate_steps(test_visitor)
      File "(...)/morelia/grammar.py", line 74, in evaluate_steps
        self._evaluate_child_steps(visitor)
      File "(...)/morelia/grammar.py", line 80, in _evaluate_child_steps
        step.evaluate_steps(visitor)
      File "(...)/morelia/grammar.py", line 226, in evaluate_steps
        self.evaluate_test_case(visitor, step_indices)  # note this works on reports too!
      File "(...)/morelia/grammar.py", line 237, in evaluate_test_case
        step.evaluate_steps(visitor)
      File "(...)/morelia/grammar.py", line 73, in evaluate_steps
        visitor.visit(self)
      File "(...)/morelia/visitors.py", line 53, in visit
        node.test_step(self._suite, self._matcher)
      File "(...)/morelia/grammar.py", line 366, in test_step
        self.evaluate(suite, matcher)
      File "(...)/morelia/grammar.py", line 362, in evaluate
        method(*args, **kwargs)
      File "test_acceptance.py", line 41, in step_the_result_should_be_on_the_screen
        self.assertEqual(int(number), self.calculator.get_result())
    AssertionError: 
      File "calculator.feature", line 11, in Scenario: Add two numbers
       Then: the result should be "121" on the screen

    121 != 120

    ----------------------------------------------------------------------
    Ran 1 test in 0.020s

    FAILED (failures=1)

More verbose
^^^^^^^^^^^^

OK. In Behaviour Driven Development participate both programmers and non-programmers
and the latter like animations and so on. So to make Morelia a little more verbose
you can pass a formatter into :py:func:`morelia.run` method.

For :py:class:`plain text formatter <morelia.formatters.PlainTextFormatter>`.


.. code-block:: python

    from morelia.formatters import PlainTextFormatter

    run(filename, self, formatter=PlainTextFormatter())

.. code-block:: console

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    Scenario: Add two numbers
        Given I have powered calculator on                       # pass  0.000s
        When I enter "50" into the calculator                    # pass  0.000s
        And I enter "70" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        Then the result should be "120" on the screen            # pass  0.001s
    Scenario: Subsequent additions
        Given I have powered calculator on                       # pass  0.000s
        When I enter "50" into the calculator                    # pass  0.000s
        And I enter "70" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        And I enter "20" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        Then the result should be "140" on the screen            # pass  0.001s
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.027s

    OK


For :py:class:`color text formatter <morelia.formatters.ColorTextFormatter>`.

.. code-block:: python

    from morelia.formatters import ColorTextFormatter

    run(filename, self, formatter=ColorTextFormatter())

.. code-block:: console

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    Scenario: Add two numbers
        Given I have powered calculator on                       # 0.000s
        When I enter "50" into the calculator                    # 0.000s
        And I enter "70" into the calculator                     # 0.000s
        And I press add                                          # 0.001s
        Then the result should be "120" on the screen            # 0.001s
    Scenario: Subsequent additions
        Given I have powered calculator on                       # 0.000s
        When I enter "50" into the calculator                    # 0.000s
        And I enter "70" into the calculator                     # 0.000s
        And I press add                                          # 0.001s
        And I enter "20" into the calculator                     # 0.000s
        And I press add                                          # 0.001s
        Then the result should be "140" on the screen            # 0.001s
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.027s

    OK

(You have to run above for yourself to see colors - sorry).

Or you can write your own formatter.

See api for :py:class:`morelia.formatters.IFormatter`.

Shortcuts
---------

In examples you've probably seen such call:


.. code-block:: python

    run(filename, verbose=True, show_all_missing=True)


``verbose`` param tries to use :py:class:`morelia.formatters.ColorTextFormatter` if avaiable in system
and fallbacks to :py:class:`morelia.formatters.PlainTextFormatter` if can't show colors.

If you pass ``show_all_missing`` parameter then Morelia would print all missing
steps instead of the first one.

.. rubric:: Footnotes

.. [#ROS] Rule of Silence - When a program has nothing surprising to say, it should say nothing http://www.faqs.org/docs/artu/ch01s06.html#id2878450
.. [#ROR] Rule of Repair - Repair what you can - but when you must fail, fail noisily and as soon as possible http://www.faqs.org/docs/artu/ch01s06.html#id2878538


