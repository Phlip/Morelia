Feature: DocStrings support

    Scenario: Scenario with docstring
        Given I have step with docstring
            """
            Docstring line1
            line2
            """
        When above step is executed
        Then it has docstring passed in _text variable
