Feature: Background support

     Morelia processes this prose and runs the results as 
     a test suite. This prose describes how background syntax can be used.

    Background:
        Given I have some background steps defined
        And step contains <when>

    Scenario: background steps are executed before scenario steps
        When scenario is executed
        Then all background steps are executed before any step defined in scenario

    Scenario: background steps are executed before every scenario
        When other scenario is executed
        Then background steps are executed again before every scenario

    Scenario: background steps and scenario's givens
        Given single scenario given step
        When scenario is executed
        Then scenario given step is executed after background steps

    Scenario: execute background steps with table
        When scenario is executed
        Then background step with <when> will be executed
            | when          |
            | some value    |

    Scenario: background steps should be run once per scenario
        When all scenarios are executed
        Then background steps will be executed once per every scenario case
