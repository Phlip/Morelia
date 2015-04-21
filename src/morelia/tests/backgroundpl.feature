Właściwość: obsługa Background
    Założenia:
        Zakładając, że step_ran was "1"
        I alt_step_ran was "0"

    Scenariusz: execute background steps
        Jeżeli I increment step_ran by "1"
        I increment alt_step_ran by "1"
        Wtedy step_ran will equal "2"
        I alt_step_ran will equal "1"

    Scenariusz: execute background steps with second scenario
        Jeżeli I increment step_ran by "1"
        I increment alt_step_ran by "1"
        Wtedy step_ran will equal "2"
        I alt_step_ran will equal "1"

    Scenariusz: execute background steps and scenario's givens
        Zakładając, że alt_step_ran was "2"
        Jeżeli I increment step_ran by "1"
        I increment alt_step_ran by "1"
        Wtedy step_ran will equal "2"
        I alt_step_ran will equal "3"
