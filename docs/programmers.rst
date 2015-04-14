Tutorial for programmers
========================

Quick usage guide
-----------------

Write feature description:

.. code-block:: cucumber

    # calculator.feature

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    
    Scenario: Add two numbers
        Given I have powered calculator on
        When I enter 50 into the calculator
        And I enter 70 into the calculator
        And I press add
        Then the result should be 120 on the screen


Create standard python's unittest[1]_ and hook Morelia in it:

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

        def step_I_enter_50_into_the_calculator(self):
            ur'I enter 50 into the calculator'

            # code
            pass

        def step_I_enter_70_into_the_calculator(self):
            ur'I enter 70 into the calculator'

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
    
        def test_addition(self):
            Parser().parse_file('calculator.feature').evaluate(self)
    
        def step_I_have_powered_calculator_on(self):
            ur'I have powered calculator on'
            self.stack = []

        def step_I_enter_a_number_into_the_calculator(self, number):
            ur'I enter (\d+) into the calculator'  # match by regexp
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

The Gherkin language
--------------------

Language used to describe features is called "Gherkin". It's a little formalized
natural language that's easy to write by non-programmers.

Each feature should be described in separate document.

Comments
^^^^^^^^

To include comments inside feature document start line with hash (#).
Everything after this to the end of line will be treated as a comment.

Language directive
^^^^^^^^^^^^^^^^^^

If comment is in the form:

.. code-block:: cucumber

   # language: en

Then feature description will be analyzed according to given native language.
All supported languages with grammar keywords are here:

    https://github.com/kidosoft/Morelia/blob/master/src/morelia/i18n.py

If there's no language directive then English is assumed.

Feature keyword
^^^^^^^^^^^^^^^

In each document should be one "Feature" keyword. After "Feature" keyword
goes name of feature and optional description:

.. code-block:: cucumber

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    
Note that "In order", "As a", and "I want" are not Morelia keywords.
That's a description. Description is free formed text although below is 
suggested form:

.. code-block:: cucumber

        In order to <goal description>
        As a <role>
        I want to <action>

That form allows to look at feature from end user's perspective.

Scenario keyword
^^^^^^^^^^^^^^^^

Each feature consists of one or more scenarios which begins with "Scenario"
keyword and scenario's name. Then goes steps describing scenario:

.. code-block:: cucumber

    Scenario: Add two numbers
        Given I have powered calculator on
        When I enter 50 into the calculator
        And I enter 70 into the calculator
        And I press add
        Then the result should be 120 on the screen

Steps
^^^^^

Each scenario consists of many steps. Steps have associated meaning:

* "Given" describe initial state of system
* "When" are used to describe actions
* "Then" are used to describe final state of system

"And" and "But" are used to enumerate more "Given", "When", "Then" steps.

Matching steps
^^^^^^^^^^^^^^

Method names from test case are matched with:

* regular expressions
* python's format-like expressions
* method names

.. code-block:: python

    # test_acceptance.py

    import unittest
    from morelia import Parser


    class CalculatorTestCase(unittest.TestCase):
    
        def test_addition(self):
            Parser().parse_file('calculator.feature').evaluate(self)
    
        def step_I_have_powered_calculator_on(self):
            ur'I have powered calculator on'
            self.stack = []

        def step_I_enter_a_number_into_the_calculator(self, number):
            ur'I enter (\d+) into the calculator'  # match by regexp
            self.stack.append(int(number))
    
        def step_I_press_add(self):  #  matched by method name
            self.result = sum(self.stack)
    
        def step_the_result_should_be_on_the_screen(self, number):
            ur'the result should be {number} on the screen'  # match by format-like string
            assert int(number) == self.result
    

Regular expressions, such as `(\d+)`, are expanded into step arguments,
such as `number` in above example.
Remember to use tight expressions, such as `(\d+)`,
not expressions like `(\d*)` or `(.*)`, to validate your input.

By analogy same matching with format-like strings. `{number}` is matched
to `numeber` argument.


Tables
^^^^^^

To DRY up a series of redundant scenarios, varying by only "payload" variables,
roll the Scenarios up into a table, using `<angles>` around the payload variable names:

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

That Scenario will unroll into a series of scenarios,
each with one value from the table inserted into their placeholders `<total>`,
`<destination>`, and `<rapid>`.
So this step method will receive each line in the "destination" column:

.. code-block:: python

    def step_the_order_will_ship_to_(self, location):
        r'the order will ship to (.*)'

(And observe that naming the placeholder the same as the method argument
is a *reeeally* good idea, but naturally unenforceable.)

Morelia Viridis will take each line of the table,
and construct a complete test case out of the Scenario steps,
running `setUp()` and `tearDown()` around them.

When keyword special behaviour
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The other step keywords (Given, And, Then, etc.) are cosmetic,
to permit good grammar. They are all aliases for Step.
The committee may eventually find specific uses for them.

The `When` keyword, however, is special. When a Scenario contains more than one When,
Morelia splits it up into one Scenario for each When block,
and runs each one separately. So the following two Feature details are equivalent...

.. code-block:: cucumber

    Scenario: Split When Blocks
        Given some setup
          And some condition
         When a first trigger occurs
         Then something good happens
    
    Scenario: Split When Blocks again
        Given some setup
          And some condition
         When another trigger occurs
         Then something else happens

...and...

.. code-block:: cucumber

    Scenario: Split When Blocks, and again
        Given some setup
          And some condition
    
         When a first trigger occurs
         Then something good happens
    
         When another trigger occurs
         Then something else happens

The second version DRYs the setup conditions.

The committee does not yet know what happens if a multi-When Scenario also contains a table, so please don't rely on whatever the current behavior is!

Here's another **sneaky snake**, which might also be a Green Tree Python (a Morelia *viridis*):

.. image:: http://zeroplayer.com/images/stuff/sneakySnake.jpg

.. rubric:: Footnotes
.. [1] More on Python's unittests https://docs.python.org/library/unittest.html


