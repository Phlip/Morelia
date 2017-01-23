@label1
Feature: Tags support

    @label2
    Scenario: Scenario with labels: 1, 2
        Given step with _labels
        When step without _labels
        Then I should get labels "1,2"

    @label3 @label4
    Scenario: Scenario with labels: 1, 3, 4
        Given step with kwargs
        When step without _labels
        Then I should get labels "1,3,4"

    @label5
    @label6
    Scenario: Scenario with labels: 1, 5, 6
        Given step with kwargs
        When step without _labels
        Then I should get labels "1,5,6"

    @label7
    Scenario: Scenario with labels: 1, 7
        Given step with kwargs
        And step with "@label8"
        When step without _labels
        Then I should get labels "1,7"
