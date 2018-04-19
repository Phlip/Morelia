Feature: DocStrings support

     Morelia processes this prose and runs the results as 
     a test suite. This prose describes how docstrings can be used to add
     larger blocks of text.

    Scenario: Scenario with docstring
        When I put docstring after step definition
            """
            Docstring line1
            line2
            """
        Then I will get docstring passed in _text variable
