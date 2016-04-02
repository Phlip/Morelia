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

Scenario: Subsequent additions
    Given I have powered calculator on
    When I enter "50" into the calculator
    And I enter "70" into the calculator
    And I press add
    And I enter "20" into the calculator
    And I press add
    Then the result should be "140" on the screen

Scenario: Add two numbers - table
    Given I have powered calculator on
    When I enter "<num1>" into the calculator
    And I enter "<num2>" into the calculator
    And I press add
    Then the result should be "<result>" on the screen
        | num1 | num2 | result |
        | 2    | 3    | 5      |
        | 4    | 5    | 9      |

