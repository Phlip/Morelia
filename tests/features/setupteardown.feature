Feature: setUp/tearDown multiply run bug

    Scenario: should run setUp only once per scenario
        Given step one

    Scenario: second scenario
        Given step two
