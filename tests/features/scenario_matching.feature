Feature: Scenario Matching
    In order to isolate scenarios in my tests with more precision
    As a test idiot
    I want to be able to specify regex patterns for scenarios and only run those tests

    Scenario: Scenario Matches 1
        Given I have powered calculator on
        When I enter "50" into the calculator
        And I enter "70" into the calculator
        And I press add
        Then the result should be "120" on the screen

    Scenario: Scenario DOESN'T MATCH!
        Given I have powered calculator on
        When I enter "4" into the calculator
        And I enter "3" into the calculator
        And I press multiply
        Then the result should be "12" on the screen

    Scenario: Scenario also DOESN'T MATCH
        Given I have powered calculator on
        When I enter "8" into the calculator
        And I enter "2" into the calculator
        And I press divide
        Then the result should be "4" on the screen

    Scenario: Scenario Matches 2
        Given I have powered calculator on
        When I enter "150" into the calculator
        And I enter "70" into the calculator
        And I press subtract
        Then the result should be "80" on the screen
