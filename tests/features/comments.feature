Feature: Comments support

    Scenario: Comment after "Step" in scenario with tables
        Given I have some comment after step without table
        # comment after step without table
        And I have interpolated <data> from table
        When I execute this scenario
        Then scenario will pass
            | data      |
            | some data |
