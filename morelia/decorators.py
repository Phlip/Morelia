# -*- coding: utf-8 -*-
"""
Decorators
----------

Sometimes you need selectively run tests. For that reason you can tag your tests:

.. code-block:: python

    # test_acceptance.py

    import unittest

    from morelia import run
    from morelia.decorators import tags


    class CalculatorTestCase(unittest.TestCase):

        @tags(['basic'])
        def test_addition(self):
            ''' Addition feature '''
            filename = os.path.join(os.path.dirname(__file__), 'add.feature')
            run(filename, self)
            # ...

        @tags(['advanced'])
        def test_substraction(self):
            ''' Substraction feature '''
            filename = os.path.join(os.path.dirname(__file__), 'substract.feature')
            run(filename, self)
            # ...

        @tags(['slow', 'advanced'])
        def test_multiplication(self):
            ''' Multiplication feature '''
            filename = os.path.join(os.path.dirname(__file__), 'multiplication.feature')
            run(filename, self)
            # ...

And run tests only for selected features:

.. code-block:: console

    $ MORELIA_TAGS=basic python -m unittest test_acceptance

    .ss
    ----------------------------------------------------------------------
    Ran 3 test in 0.018s

    OK (skipped=2)

    $ MORELIA_TAGS=advanced python -m unittest test_acceptance

    s..
    ----------------------------------------------------------------------
    Ran 3 test in 0.048s

    OK (skipped=2)

    $ MORELIA_TAGS=-slow python -m unittest test_acceptance

    ..s
    ----------------------------------------------------------------------
    Ran 3 test in 0.028s

    OK (skipped=1)

    $ MORELIA_TAGS=advanced,-slow python -m unittest test_acceptance

    s.s
    ----------------------------------------------------------------------
    Ran 3 test in 0.022s

    OK (skipped=2)
"""

import unittest

from morelia.config import get_config


def should_skip(tags_list, pattern):
    tags_list = set(tags_list)
    matching_tags = pattern.split()
    negative_tags = [tag[1:] for tag in matching_tags if tag.startswith('-')]
    positive_tags = [tag for tag in matching_tags if not tag.startswith('-')]
    if negative_tags:
        return bool(set(negative_tags) & tags_list)
    if positive_tags:
        return not set(positive_tags).issubset(tags_list)
    return False


def tags(tags_list, config=None):
    """ Skip decorated test methods or classes if tags matches.

    Tags are matched to patterns provided by config object.

    :param list tags_list: list of tags for test
    :param morelia.config.Config config: optional configuration object
    """
    if config is None:
        config = get_config()
    pattern = config.get_tags_pattern()
    return unittest.skipIf(should_skip(tags_list, pattern), 'Tags not matched')
