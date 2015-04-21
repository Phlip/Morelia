Feature: Background support
    Background:
        Given step_ran was "1"
        And alt_step_ran was "0"
        And angles_step was <background>

    Scenario: execute background steps
        When I increment step_ran by "1"
        And increment alt_step_ran by "1"
        Then step_ran will equal "2"
        And alt_step_ran will equal "1"
        Then angles_step will be string "<background>"

    Scenario: execute background steps with second scenario
        When I increment step_ran by "1"
        And increment alt_step_ran by "1"
        Then step_ran will equal "2"
        And alt_step_ran will equal "1"

    Scenario: execute background steps and scenario's givens
        Given alt_step_ran was "2"
        When I increment step_ran by "1"
        And increment alt_step_ran by "1"
        Then step_ran will equal "2"
        And alt_step_ran will equal "3"

    Scenario: execute background steps with table
        When I increment angles_step by <when>
        Then angles_step will equal <then>
            | background | when | then |
            | 1          | 2    | 3    |

