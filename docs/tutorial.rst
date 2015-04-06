For programmers
===============

Feature description
-------------------

To use it, first write a :file:`project.feature` file [1]_, in ordinary prose, like this:

.. code-block:: cucumber

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    
    Scenario: Add two numbers
        Given I have entered 50 into the calculator
        And I have entered 70 into the calculator
        When I press add
        Then the result should be 120 on the screen

Note that "In order", "As a", and "I want" are not Morelia keywords.
They are part of *Feature*'s "predicate"; its text payload.

"Given", "And", "When" and "Then" are keywords.
The words following them are executable test specifications.

Writing TestCase
----------------

Now create a standard Python's unittest [2]_ *test case*, like this:

.. code-block:: python

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

Note that Morelia does not waste anyone's time inventing a new testing back-end
just to add a layer of literacy over our testage. Steps are miniature test cases.
Your onsite customer need never know, and your unit tests and customer tests
can share their support methods. The same one test button can run all TDD and BDD tests.

Next, note that Morelia matches Steps in your Feature file to either the names
or doc-strings of *step_* methods in your test case.
And it expands regular expressions, such as `(\d+)`, into step arguments,
such as `number`. Remember to use tight expressions, such as `(\d+)`,
not loosey-goose expressions like `(\d*)` or `(.*)`, to validate your input.

When you run your TestCase, **hook** into all your feature files, like this:

.. code-block:: python

    def test_evaluate_file(self):
        from morelia import Parser
        Parser().parse_file('tests/morelia.feature').evaluate(self)

The passing steps will appear as passing test cases in your test run.

And note that Morelia calls `setUp()` and `tearDown()` around your Scenario.
Each step calls within one TestCase, so `self` can store variables between each step.

Tables
------

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

When
----

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
.. [1] File name really doesn't matter for Morelia but by conversion .feature extension is used.
.. [2] More on Python's unittests https://docs.python.org/library/unittest.html


