This example shows how to use Morelia within your project.

Morelia does not invent a wheel again. If you can run your regular unittests,
then you can run Morelia too.

Run::

    python -m unittest -v test_unit

And you're unit tests will be executed. Run the similar command with Morelia in it::

    python -m unittest -v test_acceptance

And you're acceptance (BDD) tests will be run. There's no problem to run them
all at the same time::

    python -m unittest -v test_all

If you run your tests with nose, py.test or any other test runner you can still
use it without any modifications::

    nosetsts test_all.py
    py.test test_all.py

Now go to test_acceptance.py and look how to use it and play with it freely.
