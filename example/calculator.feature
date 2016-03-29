Feature: Addition
    In order to avoid silly mistakes
    As a math idiot
    I want to be told the sum of two numbers

Scenario: Add two numbers
    Given I have powered calculator on
    When I enter "50" into the calculator
    And I enter "70" into the calculator
    And I press add
    Then the result should be "120" on the screen

Scenario: Subsequent additions zażółć gęślą jaźń
    Given I have powered calculator on
    When I enter "50" into the calculator
    And I enter "70" into the calculator
    And I press add
    And I enter "20" into the calculator
    And I press add
    Then the result should be "141" on the screen
