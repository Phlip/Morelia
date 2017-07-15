Feature: Comments support

     Morelia processes this prose and runs the results as 
     a test suite. This prose describes how comments can be applied.
     # As a general rule: any line starting with "#" (with optional leading whitespaces
     # is considered as a comment

    Scenario: Comment can be put on separate line after any step
        Given I have some comment after step on separate line
        # like this one
        Then scenario will pass

    Scenario: Comment can be put between table rows
        Given I have table with comment between rows
            | data      |
            # this is a comment between table rows
            | some data |
        Then I won't have comment in interpolated <data> from table
