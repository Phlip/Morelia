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

Scenario: Subtract two numbers
    Given I have powered calculator on
    When I enter "150" into the calculator
    And I enter "70" into the calculator
    And I press subtract
    Then the result should be "80" on the screen

Scenario: Multiply two numbers
    Given I have powered calculator on
    When I enter "4" into the calculator
    And I enter "3" into the calculator
    And I press multiply
    Then the result should be "12" on the screen

Scenario: Divide two numbers
    Given I have powered calculator on
    When I enter "8" into the calculator
    And I enter "2" into the calculator
    And I press divide
    Then the result should be "4" on the screen
