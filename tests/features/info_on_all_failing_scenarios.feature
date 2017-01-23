Feature: Information on all failing scenarios

    Scenario: 2nd and 4th failing scenario
        Given that feature with 4 scenarios has been described in file "sample.feature"
        And that test case passing 1 and 3 scenario and failing 2 and 4 has been written
        When I run test case
        Then I will get assertion error with information "2 scenarios failed, 2 scenarios passed"
        And I will get traceback of each failing scenario

    Scenario: all scenarios failing
        Given that feature with 4 scenarios has been described in file "sample.feature"
        And that test case failing all scenarios been written
        When I run test case
        Then I will get assertion error with information "4 scenarios failed, 0 scenarios passed"
        And I will get traceback of each failing scenario

    Scenario: 1st failing scenario
        Given that feature with 4 scenarios has been described in file "sample.feature"
        And that test case passing 2, 3 and 4 scenario and failing 1 has been written
        When I run test case
        Then I will get assertion error with information "1 scenario failed, 3 scenarios passed"
        And I will get traceback of each failing scenario

    Scenario: all scenarios passing
        Given that feature with 4 scenarios has been described in file "sample.feature"
        And that test case passing all scenarios been written
        When I run test case
        Then I won't get assertion error

    Scenario: 4th passing scenario
        Given that feature with 4 scenarios has been described in file "sample.feature"
        And that test case failing 1, 2 and 3 scenario and passing 4 has been written
        When I run test case
        Then I will get assertion error with information "3 scenarios failed, 1 scenario passed"
        And I will get traceback of each failing scenario

