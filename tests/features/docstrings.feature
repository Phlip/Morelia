Feature: DocStrings support

    Scenario: Scenario with docstring
        Given step with docstring
            """
            Docstring line1
            line2
            """
        When step without docstring
