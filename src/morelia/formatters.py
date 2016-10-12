"""
Formatting output
=================

Morelia complies with Unix's `Rule of Silence` [#ROS]_ so when you hook it like this:

.. code-block:: python

    run(filename, self)

and all tests passes it would say nothing:

.. code-block:: console

    $ python -m unittest test_acceptance
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.028s

    OK

(here's only information from test runner)

But when something went wrong it would complie with Unix's `Rule of Repair` [#ROR]_
and fail noisily:

.. code-block:: console

    F
    ======================================================================
    FAIL: test_addition (test_acceptance.CalculatorTestCase)
    Addition feature
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "test_acceptance.py", line 45, in test_addition
        run(filename, self)
      File "(..)/morelia/__init__.py", line 22, in run
        return ast.evaluate(suite, **kwargs)
      File "(...)/morelia/grammar.py", line 36, in evaluate
        feature.evaluate_steps(test_visitor)
      File "(...)/morelia/grammar.py", line 74, in evaluate_steps
        self._evaluate_child_steps(visitor)
      File "(...)/morelia/grammar.py", line 80, in _evaluate_child_steps
        step.evaluate_steps(visitor)
      File "(...)/morelia/grammar.py", line 226, in evaluate_steps
        self.evaluate_test_case(visitor, step_indices)  # note this works on reports too!
      File "(...)/morelia/grammar.py", line 237, in evaluate_test_case
        step.evaluate_steps(visitor)
      File "(...)/morelia/grammar.py", line 73, in evaluate_steps
        visitor.visit(self)
      File "(...)/morelia/visitors.py", line 53, in visit
        node.test_step(self._suite, self._matcher)
      File "(...)/morelia/grammar.py", line 366, in test_step
        self.evaluate(suite, matcher)
      File "(...)/morelia/grammar.py", line 362, in evaluate
        method(*args, **kwargs)
      File "test_acceptance.py", line 41, in step_the_result_should_be_on_the_screen
        self.assertEqual(int(number), self.calculator.get_result())
    AssertionError:
      File "calculator.feature", line 11, in Scenario: Add two numbers
       Then: the result should be "121" on the screen

    121 != 120

    ----------------------------------------------------------------------
    Ran 1 test in 0.020s

    FAILED (failures=1)

Verbosity
---------

In Behaviour Driven Development participate both programmers and non-programmers
and the latter like animations and so on. So to make Morelia a little more verbose
you can pass a `verbose=True` into :py:func:`morelia.run` method.

.. code-block:: python

    run(filename, self, verbose=True)

.. code-block:: console

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    Scenario: Add two numbers
        Given I have powered calculator on                       # pass  0.000s
        When I enter "50" into the calculator                    # pass  0.000s
        And I enter "70" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        Then the result should be "120" on the screen            # pass  0.001s
    Scenario: Subsequent additions
        Given I have powered calculator on                       # pass  0.000s
        When I enter "50" into the calculator                    # pass  0.000s
        And I enter "70" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        And I enter "20" into the calculator                     # pass  0.000s
        And I press add                                          # pass  0.001s
        Then the result should be "140" on the screen            # pass  0.001s
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.027s

    OK

With ``verbose=True`` Morelia tries to use :py:class:`morelia.formatters.ColorTextFormatter` if avaiable in system
and fallbacks to :py:class:`morelia.formatters.PlainTextFormatter` if can't show colors.

You can explicity pass formatter you want use:

.. code-block:: python

    from morelia.formatters import ColorTextFormatter

    run(filename, self, formatter=ColorTextFormatter())

.. code-block:: console

    Feature: Addition
        In order to avoid silly mistakes
        As a math idiot
        I want to be told the sum of two numbers
    Scenario: Add two numbers
        Given I have powered calculator on                       # 0.000s
        When I enter "50" into the calculator                    # 0.000s
        And I enter "70" into the calculator                     # 0.000s
        And I press add                                          # 0.001s
        Then the result should be "120" on the screen            # 0.001s
    Scenario: Subsequent additions
        Given I have powered calculator on                       # 0.000s
        When I enter "50" into the calculator                    # 0.000s
        And I enter "70" into the calculator                     # 0.000s
        And I press add                                          # 0.001s
        And I enter "20" into the calculator                     # 0.000s
        And I press add                                          # 0.001s
        Then the result should be "140" on the screen            # 0.001s
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.027s

    OK

(You have to run above for yourself to see colors - sorry).

Or you can write your own formatter.

Missing steps
-------------

By default Morelia prints all missing steps if it finds out that some steps
are missing. If you pass ``show_all_missing=False`` then only first missing step
will be shown. It can be usefull when working with features with many steps.

Formatter Classes
-----------------

"""

from abc import ABCMeta, abstractmethod
import sys

from .grammar import Step, Feature

colors = {
    'normal': u'\x1b[30m',
    'fail': u'\x1b[31m',
    'error': u'\x1b[31m',
    'pass': u'\x1b[32m',
    'reset': u'\x1b[0m',
}


class IFormatter(object):

    ''' Abstract Base Class for all formatters. '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def output(self, node, line, status, duration):
        ''' Method called after execution each step.

        :param INode node: node representing step
        :param str line: text of executed step
        :param str status: execution status
        :param float duration: step execution duration
        '''
        pass  # pragma: nocover


class NullFormatter(IFormatter):

    ''' Formatter that... do nothing. '''

    def output(self, node, line, status, duration):
        ''' See :py:meth:`IFormatter.output` '''

        pass


class PlainTextFormatter(IFormatter):

    ''' Formatter that prints all executed steps in plain text to a given stream. '''

    def __init__(self, stream=None):
        ''' Initialize formatter.

        :param file stream: file-like stream to output executed steps
        '''
        self._stream = stream if stream is not None else sys.stderr

    def output(self, node, line, status, duration):
        ''' See :py:meth:`IFormatter.output` '''

        if isinstance(node, Feature):
            self._stream.write('\n')
        if isinstance(node, Step):
            status = status.lower()
            text = '%-60s # %-5s %.3fs\n' % (
                line.strip('\n'),
                status,
                duration,
            )
        else:
            text = '%s\n' % line.strip('\n')
        self._stream.write(text)
        self._stream.flush()


class ColorTextFormatter(PlainTextFormatter):

    ''' Formatter that prints all executed steps in color to a given stream. '''

    def output(self, node, line, status, duration):
        ''' See :py:meth:`IFormatter.output` '''

        if isinstance(node, Feature):
            self._stream.write('\n')
        if isinstance(node, Step):
            status = status.lower()
            text = '%s%-60s # %.3fs%s\n' % (
                colors[status],
                line.strip('\n'),
                duration,
                colors['reset']
            )
        else:
            text = '%s\n' % line.strip('\n')
        self._stream.write(text)
        self._stream.flush()
