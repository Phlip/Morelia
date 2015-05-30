.. _writers-tutorial:

Tutorial for scenario writers
=============================

Scenarios are meant as tool for easier communication between developers, QA
and business participants. This tutorial is written with non-programmers in mind.

Scenarios are written in a little formalized natural language.
Programmers expect that each software feature will be written in separate file.

Language
--------

Features can be written in your native language.  It is much easier
to describe what you expect from software in language that is well known
for all participants. E.g. if all participants use Japanese at the beginning
of feature file write::

    # language: ja

Language code is two-letter code as listed in `ISO 639-1`_ standard.
If you skip that step then English will be assumed.

Feature
-------

Next, write a name of feature that you need.

.. code-block:: cucumber

    # language: en

    Feature: Add an item to basket

"Feature" is a keyword and have to be used literally. Every language has it's
own set of keywords. E.g. for Spanish (es) it would be look like:

.. code-block:: cucumber
   
   # language: es
   
   Característica: Agregar un elemento a la cesta

Next goes introductory description. It's an optional free formed text.
If you want your programmer to better understand what you expect from him
please try to follow a schema:

.. code-block:: cucumber

        In order to <goal description>
        As a <role>
        I want to <action>

The goal description is essential for programmer to understand in what is
a goal of a whole feature and why you want this feature to be added to software.
It allows him to structure software in a way that it'll
be easier in future add new features and modify existing ones. E.g.:

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item

would tell him that in the end an item added to basked will be sold.

Describing role should help both you and programmer to start thinking from
role's perspective. E.g.:

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item
        As a logged user

From that point both you and programmer should start thinking like a logged
user and describe actions in first person as logged user.

Next describe what you as a "role" want to do:

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item
        As a logged user
        I want to add items into basket

In this part you can also write other non-behavioral information for programmer. 

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item
        As a logged user
        I want to add items into basket

        Adding item to basket should not reload page

Scenario
--------

Each feature consists of one or more scenarios.  Each scenario describes
what <role> is doing, step by step, to realize feature.
Scenario starts with keyword "Scenario" in your chosen language (e.g. "Scénario"
in French) followed by short description of that case:

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item
        As a logged user
        I want to add items into basket

        Adding item to basket should not reload page

    Scenario: Adding from item's description page

In above example a logged user will visit item's description page
and add item to basket.

Next you write each action that you would perform if you were a <role>. Use
a schema:

.. code-block:: cucumber

        Given <precondition that have to be met>
        And  <more preconditions>
        But  <more preconditions>
        ...

        When <action that have to be done>
        And <next action>
        But <next action>
        ...

        Then <observable result of actions>
        And <more results>
        But <more results>
        ...

"Given", "When", "Then", "And" and "But" are all keywords. In our online store example
we could write something like this:

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item
        As a logged user
        I want to add items into basket

        Adding item to basket should not reload page

    Scenario: Adding from item's description page

        Given that the "Alice in Wonderland book" is in online store
        And that item costs "50" USD
        And shipping costs of that item are "5" USD
        And in my basket are "0" items
        And value of my basket is "0" USD
        And shipping costs are "0" USD

        When I visit an item description page
        And I click button "Add to basket"

        Then I see message "'Alice in Wonderland' has been added to basket"
        And I see "1" items in my basket
        And value of my basket become "50" USD
        And shipping costs become "5" USD

After "Given" you define what is expected starting state (item is in store;
basked is empty). After "When" you write what <role> is performing
(logged user visits item page and clicks on button). And after "Then" you write
what is ending state (displayed message, one item in basket). "And" and "But"
are used to write more actions and conditions in block "Given", "When", "Then".

Alternatives
------------

If there are alternative paths to achieve feature goals you should write scenarios
for them too:

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item
        As a logged user
        I want to add items into basket

        Adding item to basket should not reload page

    Scenario: Adding from item's description page

        Given that the "Alice in Wonderland book" is in online store
        And that item costs "50" USD
        And shipping costs of that item are "5" USD
        And in my basket are "0" items
        And value of my basket is "0" USD
        And shipping costs are "0" USD

        When I visit an item description page
        And I click button "Add to basket"

        Then I see message "'Alice in Wonderland' has been added to basket"
        And I see "1" items in my basket
        And value of my basket become "50" USD
        And shipping costs become "5" USD

    Scenario: Adding item from search result page

        Given that the "Alice in Wonderland book" is in online store
        And that item costs "50" USD
        And shipping costs of each item is "5" USD
        And in my basket are "0" items
        And value of my basket is "0" USD
        And shipping costs are "0" USD

        When I visit a search page
        And I enter "Alice in Wonderland" in search box
        And I click button "Search"
        And I see button "Add to basket" next to item "Alice in Wonderland"
        And I click button "Add to basket"

        Then I see message "'Alice in Wonderland' has been added to basket"
        And I see "1" items in my basket
        And value of my basket become "50" USD
        And shipping costs become "5" USD


Tables
------

Sometimes you want give more sample values to show expected behaviour.
E.g. if value of basked exceed 100 USD you can give your customers discount
on shipping costs. Let say that above 100 USD shipping costs are 0 USD.
You can write second scenario for this case:

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item
        As a logged user
        I want to add items into basket

        Adding item to basket should not reload page

    Scenario: Adding from item's description page

        Given that the "Alice in Wonderland book" is in online store
        And that item costs "50" USD
        And shipping costs of that item are "5" USD
        And in my basket are "0" items
        And value of my basket is "0" USD
        And shipping costs are "0" USD

        When I visit an item description page
        And I click button "Add to basket"

        Then I see message "'Alice in Wonderland' has been added to basket"
        And I see "1" items in my basket
        And value of my basket become "50" USD
        And shipping costs become "5" USD

    Scenario: Adding from item's description page without shipping costs

        Given that the "Alice in Wonderland book" is in online store
        And that item costs "50" USD
        And shipping costs of that item are "5" USD
        And in my basket are "2" items
        And value of my basket is "90" USD
        And shipping costs are "5" USD

        When I visit an item description page
        And I click button "Add to basket"

        Then I see message "'Alice in Wonderland' has been added to basket"
        And I see "3" items in my basket
        And value of my basket become "140" USD
        And shipping costs become "0" USD

    Scenario: Adding item from search result page
        # ...

When more such rules appear sometimes it's easier to make a table.
Above example can be shortened:

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item
        As a logged user
        I want to add items into basket

        Adding item to basket should not reload page

    Scenario: Adding from item's description page

        Given that the "Alice in Wonderland book" is in online store
        And that item costs <cost> USD
        And shipping costs of each item is "5" USD
        And in my basket are <initial_items> items
        And value of my basket is <initial_value> USD
        And shipping costs are <initial_shipping> USD

        When I visit an item description page
        And I click button "Add to basket"

        Then I see message "'Alice in Wonderland' has been added to basket"
        And I see <items> items in my basket
        And value of my basket become <value> USD
        And shipping costs become <shipping> USD

            | cost | initial_items | initial_value | initial_shipping | items | value | shipping |
            | 50   | 0             | 0             | 0                | 1     | 50    | 5        |
            | 50   | 2             | 90            | 10               | 3     | 140   | 0        |

    Scenario: Adding item from search result page
        # ...

Names within `<angles>` will be replaced with values from rows
in table. You can easily extend table for other special cases adding new rows.

Comments
--------

When you want to add some comments inside features file, just write in a new
line beginning with "#":

.. code-block:: cucumber

    Feature: Add an item to basket

        In order to buy an item
        As a logged user
        I want to add items into basket

        Adding item to basket should not reload page

    Scenario: Adding from item's description page

        Given that the "Alice in Wonderland book" is in online store
        And that item costs <cost> USD
        And shipping costs of each item is "5" USD
        And in my basket are <initial_items> items
        And value of my basket is <initial_value> USD
        And shipping costs are <initial_shipping> USD

        When I visit an item description page
        # see description page mockup in file "description_page.jpg"
        And I click button "Add to basket"

        Then I see message "'Alice in Wonderland' has been added to basket"
        And I see <items> items in my basket
        And value of my basket become <value> USD
        And shipping costs become <shipping> USD

            | cost | initial_items | initial_value | initial_shipping | items | value | shipping |
            | 50   | 0             | 0             | 0                | 1     | 50    | 5        |
            | 50   | 2             | 90            | 10               | 3     | 140   | 0        |


.. _ISO 639-1: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
