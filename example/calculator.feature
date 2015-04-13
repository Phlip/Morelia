Feature: Addition
    In order to avoid silly mistakes
    As a math idiot
    I want to be told the sum of two numbers

Scenario: Add two numbers
    Given I have powered calculator on
    When I have entered 50 into the calculator
    And I have entered 70 into the calculator
    And I press add
    Then the result should be 120 on the screen

    # Scenario: Subsequent additions
    #     Given I have powered calculator on
    #     When I have entered 50 into the calculator
    #     And I have entered 70 into the calculator
    #     And I press add
    #     And I have entered 20 into the calculator
    #     And I press add
    #     Then the result should be 140 on the screen
