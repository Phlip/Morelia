@label1
Feature: Tags support

    @label2
    Scenario: Scenario with labels: 1, 2
        Given step with _labels
        When step without _labels

    @label3 @label4
    Scenario: Scenario with labels: 1, 3, 4
        Given step with kwargs
        When step without _labels
