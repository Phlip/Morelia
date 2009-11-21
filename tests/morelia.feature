Feature: Morelia Viridis puts the squeeze on your features.

         Morelia processes this prose and runs the results as 
         a test suite, with strings passed into each test case
         as data to evaluate

Scenario: Match prose steps to Python steps by name
    Step: evaluate_step_by_doc_string

Scenario: Fail to match prose if feature file has bad strings
    Step: fail_without_enough_function_name
    Step: fail_step_without_enough_doc_string
    #  comments don't suck

Scenario: When we challenge Morelia with a Step with no matching
          entry in your test suite, supply a helpful error message
    Given a feature file with "Given your nose is on fire"
    When Moralia evaluates the file
    Then it prints a diagnostic containing "    def step_your_nose_is_on_fire"
    And the second line contains "your nose is on fire"

Scenario: when did Bow Wow Wow become classic rock?
    Given: adventure of love - love and <culture>
        | culture  |
        | radio    |
        | g-string |
        | battery  |
        | driven   |
    When Moralia evaluates this
    Then "culture" contains ['radio', 'g-string', 'battery', 'driven']

