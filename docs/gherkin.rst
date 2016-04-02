.. _gherkin:

Gherkin language reference
==========================

Language used to describe features is called "Gherkin". It's a little formalized
natural language that's easy to write by non-programmers.

Each feature should be described in separate document.

Comments
--------

To include comments inside feature document start line with hash (#).
Everything after this to the end of line will be treated as a comment.

.. code-block:: cucumber

   # this line is a comment

Language directive
------------------

If a comment looks like:

.. code-block:: cucumber

   # language: de

Then feature description will be analyzed according to given native language.
All supported languages with grammar keywords are here:

    https://github.com/kidosoft/Morelia/blob/master/src/morelia/i18n.py

If there's no language directive then English is assumed.


Feature keyword
---------------

In each document should be one and only one "Feature" keyword.
After "Feature" keyword goes name of a feature and optional description:

.. code-block:: cucumber

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    
Note that "In order", "As a", and "I want" are not keywords.
That's a description. Description is free formed text although below is 
suggested form:

.. code-block:: cucumber

        In order to <goal description>
        As a <role>
        I want to <action>

That form allows to look at feature from end user's perspective.

Scenario keyword
----------------

Each feature consists of one or more scenarios. Each scenario begins
with "Scenario" keyword and it's name. Then go steps describing scenario:

.. code-block:: cucumber

    Scenario: Add two numbers
        Given I have powered calculator on
        When I enter "50" into the calculator
        And I enter "70" into the calculator
        And I press add
        Then the result should be "120" on the screen

.. _steps:

Steps
-----

Each scenario consists of many steps. Steps have associated meaning:

* "Given" describes initial state of system
* "When" is used to describe actions
* "Then" is used to describe final state of system

"And" and "But" are used to enumerate more "Given", "When", "Then" steps.

It is suggested that sentences in "Given" part should be written in past tense.
"When" part should be written in present tense and "Then" in future tense.

.. note:: **For programmers**

   For information how methods are matched to steps see :ref:`matching-steps`.

Background keyword
------------------

If you have to repeat the same subset of "Given" steps in all of your scenarios
you can use "Background" keyword. "Given" steps in "Background" are run as the
very first steps in each scenario. E.g. instead of writing:

.. code-block:: cucumber

    Scenario: Some scenario
        Given some setup
          And some condition
         When a first trigger occurs
         Then something good happens
    
    Scenario: Some other scenario
        Given some setup
          And some condition
         When another trigger occurs
         Then something else happens

you can write:

.. code-block:: cucumber

    Background:
        Given some setup
          And some condition
    
    Scenario: Some scenario
         When a first trigger occurs
         Then something good happens
    
    Scenario: Some other scenario
         When another trigger occurs
         Then something else happens

.. note:: **For programmers**

   Refuse temptation to put into background steps that you need to perform
   in order to set up tests, which are of no use for scenario writer (e.g. "Set up database")
   Remember that you use :py:class:`TestCases <unittest.TestCase>` so you can use
   :py:meth:`setUp <unittest.TestCase.setUp>`/:py:meth:`tearDown <unittest.TestCase.tearDown>` methods!

Tables
------

To DRY [#DRY]_ up a series of redundant scenarios, varying by only "payload" variables,
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

That Scenario will unroll into a series of 12 scenarios,
each with one value from the table inserted into their placeholders `<total>`,
`<destination>`, and `<rapid>`.

You can use many tables. It would be equivalent of permutation of all given rows.

Example
^^^^^^^

Below scenario:

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

Is equvalent of series of scenarios:

.. code-block:: cucumber

    Scenario: orders above $100.00 to the continental US get free ground shipping
      When we send an order totaling $<total>, with a 12345 SKU, to our warehouse
       And the order will ship to <destination>
       And we choose that delivery should be <speed>
      Then the ground shipping cost is $<cost>
    
           | speed   |  total | destination  |  cost |
    
           | rapid   |  98.00 | Rhode Island |  8.25 |
           | rapid   | 101.00 | Rhode Island |  0.00 |
           | rapid   |  99.00 | Kansas       |  8.25 |
           | regular |  98.00 | Rhode Island |  8.25 |
           | regular | 101.00 | Rhode Island |  0.00 |
           | regular |  99.00 | Kansas       |  8.25 |

In above example 2 * 3 = 6 different scenarios would be generated.

.. note:: **Compatibility**

   For compatibility with other Behavior Driven Development tools you
   can use "Scenario Outline" keyword instead of "Scenario" and mark table
   with "Examples" keyword if you prefer. Morelia would not enforce you to do that.

.. note:: **For programmers**

   For information how methods are matched to steps with tables see :ref:`matching-tables`.

Doc Strings
-----------

Sometimes you need to include some larger chunks of text in steps as data.
In order to accomplish this you can use doc-strings syntax:

.. code-block:: cucumber

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    
    Scenario: Add two numbers
        Given I have powered calculator on
        When I enter "50" into the calculator
        And I enter "70" into the calculator
        And I press add
        Then I would see on the screen
            """
            Calculator example
            ==================
             50
            +70
            ---
            120
            """

Text enclosed within tripple double-quotes will be attached as step's data.

.. note:: **For programmers**

   Look at :ref:`matching-docstrings` for information how to access data in steps.


Labels
------

Each feature or scenario can be labeled:

.. code-block:: cucumber

    @web
    @android @ios
    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    
    @wip
    Scenario: Add two numbers
        Given I have powered calculator on
        When I enter "50" into the calculator
        And I enter "70" into the calculator
        And I press add
        Then the result should be "120" on the screen

Labels are inherited. In above example all steps will be labeled
with "web", "android", "ios", "wip".
Labels allows to implement custom logic depending on labels given.

.. note:: **For programmers**

   Look at :ref:`labels-matching` for information how to access labels in steps.

.. image:: http://zeroplayer.com/images/stuff/sneakySnake.jpg

.. rubric:: Footnotes

.. [#DRY] Don't repeat yourself http://en.wikipedia.org/wiki/Don%27t_repeat_yourself
