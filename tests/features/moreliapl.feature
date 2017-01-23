Właściwość: Morelia Viridis puts the squeeze on your features.

         Morelia processes this prose and runs the results as 
         a test suite, with strings passed into each test case
         as data to evaluate

Scenariusz: Add two numbers
  Zakładając, że I have entered 50 into the calculator
    I I have entered 70 into the calculator
  Gdy I press add
   Wtedy the result should be 120 on the screen

Scenariusz: When we challenge Morelia with a Step with no matching
          entry in your test suite, supply a helpful error message
    Zakładając, że a feature file with "Zakładając, że your nose is on fire"
    Gdy Morelia evaluates the file
    Wtedy it prints a diagnostic containing "    def step_your_nose_is_on_fire"
    I the second line contains "your nose is on fire"

Scenariusz: When we challenge Morelia with a Step with a linefeed in it
          the default example replaces the linefeed with a space
    Zakładając, że a feature file with "Zakładając, że no line
                                          feeds"
    Gdy Morelia evaluates the file
    Wtedy it prints a diagnostic containing "    def step_no_line_feeds"
    I the second line contains "no line\nfeeds"

Scenariusz: Fail to match prose if feature file has bad strings
    Step: fail_without_enough_function_name
    Step: fail_step_without_enough_doc_string

Scenariusz: when did Bow Wow Wow become classic rock?
    Zakładając, że: adventure of love - love and <culture>
    
        | culture  
        
        | radio    
        | g-string 
        | battery  
        | driven     |  # note the trailing pipe is cosmetic, and required for comments

    Gdy Morelia evaluates this
    Wtedy "culture" contains ['radio', 'g-string', 'battery', 'driven']
      I the step keyword is Zakładając, że

Scenariusz: Convert source predicates into their matching regular expressions
   Zakładając, że a source file with a <predicate>
   Gdy we evaluate the file
   Wtedy we convert it into a <suggestion>
    I add <extra> arguments
   
       |   predicate       |   suggestion           |  extra      |
       
       | tastes great      | r'tastes great'        |             |
       | less filling      | r'less filling'        |             |
       | line\nfeed        | r'line\nfeed'          |             |
       | tick'ed'          | r'tick\'ed\''          |             |
       | tastes   great    | r'tastes\s+great'      |             |
       | argu<ment>al      | r'argu(.+)al'          | , ment      |
       | arg<u>ment<al>    | r'arg(.+)ment(.+)'     | , u, al     |
       | str"ing"          | r'str"([^"]+)"'        | , ing       |
       | "str"i"ngs"       | r'"([^"]+)"i"([^"]+)"' | , str, ngs  |
       | zażółć gęślą jaźń | r'zażółć gęślą jaźń'   |             |
#      | pipe \| me      | r'pipe \\\| me'          |             |

Scenariusz: Raise useful errors with incomplete files
  Gdy a file contains <statements>, it produces <diagnostics>
  
    |    statements       |   diagnostics

    |  Właściwość yo         | Feature without Scenario(s)

    |  Właściwość comp-      \
       Właściwość placent    | Only one Feature per file

    | Właściwość    resist   \
        Scenariusz syntax   \
          Step   errors   | Scenariusz: syntax

    |  Właściwość in da      \
         Step zone        | Feature without Scenario(s)

    |  Właściwość: Add two numbers                     \
       Scenariusz: Add two numbers                     \
        Zakładając, że I have entered 50 into the calculator  \
          I I have entered 70 into the calculator  \
         Gdy I press add                            \
         Wtedy the result should be 121 on the screen | the result should be

    |  Właściwość yo         \
         Scenariusz dude    \
           Zakładającfoo       | Scenario without step

    |  Właściwość yo         \
         Scenariusz dude    | Scenario without step(s) - Step, Given, When, Then, And, or #


Scenariusz: Match prose steps to Python steps by name
    Step: evaluate_step_by_doc_string
