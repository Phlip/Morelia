Installation
============

In order to install Morelia, make sure Python is installed. Morelia was tested
with:

    * Python 2.7
    * Python 3.3
    * Python 3.4
    * Python 3.5

Using pip
---------

To install run:

.. code-block:: console

    pip install Morelia
    
To update an already installed verision:

.. code-block:: console

    pip install -U Morelia


You can use `easy_install` in place of `pip` as well:

.. code-block:: console

    easy_install install -U Morelia


.. note::

   If you haven't pip read `pip installation informations`_.
   


Using a Source Distribution
---------------------------

.. code-block:: cucumber

    Scenario: installation with source distribution

        Given that source distribution was published on pypi
        When you download source distribution from pypi
        And unpack it
        And enter into directory "Morelia-<version>"
        And run "python setup.py install"
        Then you will have Morelia installed.

Or in short: Download and extract source distribution from pypi_ and run:

.. code-block:: console

   python setup.py install

Using the Github Repository
---------------------------

To install the newest version from the `Github repository`_ run:

.. code-block:: console

    pip install git+https://github.com/kidosoft/Morelia

.. _`Github repository`: https://github.com/kidosoft/Morelia
.. _pip installation informations:  https://pip.pypa.io/en/latest/installing.html
.. _pypi: https://pypi.python.org/pypi/Morelia/
