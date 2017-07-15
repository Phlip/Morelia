@feature_label
Feature: Labels support

    @scenario_label
    Scenario: Scenario with labels
        When step which accepts _labels variable is executed
        Then it will get labels "feature_label,scenario_label"

    @label1 @label2
    Scenario: Scenario with multiply labels
        When step which accepts _labels variable is executed
        Then it will get labels "feature_label,label1,label2"

    @scenario_label
    Scenario: Scenario with steps that do not accept _labels
        When step which does not accepts _labels variable is executed
        Then it will not get any labels
