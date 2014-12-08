import sys, os

from fabric.api import *
import time
import os
import fabfile

def _sh(cmd):
    local(cmd, capture=False)

def clean_pyc_files():
    'erase them all, because they bug us'

    _sh('find . -name \*.pyc -exec rm {} \;')

def autotest(cmd='fab test', sleep=1):
    """
    spin until you change a file, then run the tests

    It considers the fabfile.py directory as the project root directory, then
    monitors changes in any inner python files.

    Usage:

       fab autotest

    This is based on Jeff Winkler's nosy script.
    """

    def we_like(f):
        return f.endswith('.py') # or f.endswith('.html') or f.endswith('.json')

    def checkSum():
        '''
        Return a long which can be used to know if any .py files have changed.
        Looks in all project's subdirectory.
        '''

        def hash_stat(file):
            from stat import ST_SIZE, ST_MTIME
            stats = os.stat(file)
            return stats[ST_SIZE] + stats[ST_MTIME]

        hash_ = 0
        base = os.path.dirname(fabfile.__file__)

        for zone in (base, base + '/webcube/', base + '/simplecart/'):
            for root, dirs, files in os.walk(zone):
                # only python, json, & html files interest us
                files = [os.path.join(root, f) for f in files if we_like(f)]
                hash_ += sum(map(hash_stat, files))

        return hash_

    val = 0

    while(True):
        actual_val = checkSum()

        if val != actual_val:
            val = actual_val
            os.system(cmd)

        time.sleep(sleep)

def test(extra=''):
    'run the short test batch for this project'

    _sh('python tests/morelia_suite.py')
    _sh('python2.5 tests/morelia_suite.py')
    _sh('python2.6 tests/morelia_suite.py')
    _sh('git commit -am developing')

def ci():
    'stick it in GitHub'

    test()
    _sh('git push origin master')

def up():
    'stick it in Pypi'

    ci()
    with cd('morelia'):  _sh('python setup.py sdist upload')

def todo():
    'nag messages from u to u'

    _sh('git grep TO'+'DO `find . -name *.py` `find . -name *.feature` ')
