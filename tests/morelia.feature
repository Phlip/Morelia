Feature: Morelia Viridis puts the squeeze on your features.

         Morelia processes this prose and runs the results as 
         a test suite, with strings passed into each test case
         as data to evaluate

Scenario: Add two numbers
  Given I have entered 50 into the calculator
    And I have entered 70 into the calculator
  When I press add
   Then the result should be 120 on the screen
     
#  TODO  display all missing steps not just the first

Scenario: Match prose steps to Python steps by name
    Step: evaluate_step_by_doc_string

Scenario: Fail to match prose if feature file has bad strings
    Step: fail_without_enough_function_name
    Step: fail_step_without_enough_doc_string
    
    #  Note: comments don't suck!

Scenario: When we challenge Morelia with a Step with no matching
          entry in your test suite, supply a helpful error message
    Given a feature file with "Given your nose is on fire"
    When Moralia evaluates the file
    Then it prints a diagnostic containing "    def step_your_nose_is_on_fire"
    And the second line contains "your nose is on fire"

#  TODO document that we permit matches across one line!
#  CONSIDER  document that the trailing pipe is cosmetic!

Scenario: when did Bow Wow Wow become classic rock?
    Given: adventure of love - love and <culture>
        | culture  
        | radio    
        | g-string 
        | battery  
        | driven   
    When Moralia evaluates this
    Then "culture" contains ['radio', 'g-string', 'battery', 'driven']
      And the step concept is Given

Scenario: Convert source predicates into their matching regular expressions
   Given a source file with a <predicate>
   When we evaluate the file
   Then we convert it into a <suggestion>
    And add <extra> arguments
   
       |   predicate     |   suggestion           |  extra      |
       
       | tastes great    | r'tastes great'        |             |
       | less filling    | r'less filling'        |             |
       | line\nfeed      | r'line\nfeed'          |             |
       | tick'ed'        | r'tick\'ed\''          |             |
       | argu<ment>al    | r'argu(.+)al'          | , ment      |
       | arg<u>ment<al>  | r'arg(.+)ment(.+)'     | , u, al     |
       | str"ing"        | r'str"([^"]+)"'        | , ing       |
       | "str"i"ngs"     | r'"([^"]+)"i"([^"]+)"' | , str, ngs  |
       
#      | pipe \| me      | r'pipe \\\| me'        |             |
       
#  TODO escape a pipe!

Scenario: Raise useful errors with incomplete files
  When a file contains <statements>, produce <diagnostics>
  
    |  statements                 |  diagnostics

    |  Feature yo                 | Feature without Scenario(s)
    |  Feature yo\nScenario dude  | Scenario without step(s) - Step, Given, When, Then, And
    
    # TODO , |, or #
  