Feature: Comments support

     Morelia processes this prose and runs the results as 
     a test suite. This prose describes how comments can be applied.
     # As a general rule: any line starting with "#" (with optional leading whitespaces
     # is considered as a comment

    Scenario: Comment can be put on separate line after any step
        Given I have some comment after step on separate line
        # like this this one
        Then scenario will pass

    Scenario: Comment can be put after row in table on the same line
        Given I have some comment after row in table
        And I have interpolated <data> from table
        When I execute this scenario
        Then scenario will pass
            | data      | # this is unusual comment, as it can be put in the same line as data row
            | some data |

    Scenario: Comment can be put between table rows
        Given I have some comment after step without table
        And I have interpolated <data> from table
        When I execute this scenario
        Then scenario will pass
            | data      |
            # this is a comment between table rows
            | some data |
