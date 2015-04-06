# -*- coding: utf-8 -*-
import glob
import os
import sys

from paver.easy import *  # noqa
try:
    import paver.doctools  # noqa
except ImportError:
    pass
sys.path.append('.')

options(
    project=Bunch(
        name='morelia',
        package_name='morelia',
    ),
    sphinx=Bunch(
        builddir="_build",
        apidir=None,
    ),
    coverage=Bunch(
        omit=[
            'pavement.py',
            'setup.py',
            'example/*',
        ]
    ),
)


@task
def cleanup():
    """ Removes generated files. """
    sh('rm -rf build', ignore_error=True)
    sh('rm -rf dist', ignore_error=True)
    sh('rm -rf */*.egg-info', ignore_error=True)
    sh('rm -rf htmlcov', ignore_error=True)
    sh('rm -rf docs/_build', ignore_error=True)
    sh('rm .coverage.*', ignore_error=True)
    sh("find . -name '*.pyc' -delete", ignore_error=True)
    sh("find . -name '__pycache__' -delete", ignore_error=True)


@task
def kwalitee(options):
    """ Check for kwalitee. """
    sh('flake8 src')
    sh('pep257 src', ignore_error=True)


@task
def sdist():
    """ Generate source distribution. """
    sh('python setup.py sdist -q')


@task
def bdist_wheel():
    """ Generate binary distribution. """
    sh('python setup.py bdist_wheel --universal -q')


@task
@needs('sdist', 'bdist_wheel')
def build():
    """ Build packages. """
    pass


@task
@needs('build')
def test_install(options):
    """ Test installation of packages. """
    distfiles = glob.glob('dist/*')
    venv_bin_dir = '.tox/status/bin'
    pip_path = os.path.join(venv_bin_dir, 'pip')
    python_path = os.path.join(venv_bin_dir, 'python')
    for idx, distfile in enumerate(distfiles):
        try:
            # install package
            sh('%s install -q %s' % (pip_path, distfile))
            # test package installation
            sh('%s -c "import %s"' % (python_path, options.name))
        finally:
            # uninstall
            sh('%s uninstall -q -y %s' % (pip_path, options.package_name), ignore_error=True)


@task
def test_all(options):
    """ Run tests in different environtemtns. """
    sh('tox')


@task
@needs('cleanup', 'kwalitee', 'test_all', 'test_install', 'html')
def pre_release(options):
    """ Check project before release. """
    pass


@task
@cmdopts([
    ("path=", "p", "Docs path"),
])
@needs('cleanup', 'html')
def publish_docs(options):
    """ Uploads docs to server. """
    path = options.get('path', None)
    if path is None:
        path = os.environ.get('DOCS_PATH', '')
    sh('''sed -i '' 's/href="\(http:\/\/sphinx-doc.org\)/rel="nofollow" href="\\1"/' docs/_build/html/*.html''')
    sh('rsync -av docs/_build/html/ %s/%s/' % (path, options.package_name))


@task
def sign_dist(options):
    for distfile in glob.glob('dist/*'):
        if distfile.endswith('.tar.gz') or distfile.endswith('.whl'):
            sh('gpg --detach-sign -a %s' % distfile)


@task
def twine_upload(options):
    sh('twine upload dist/*')


@task
@needs('cleanup', 'build', 'html', 'sign_dist', 'twine_upload', 'publish_docs')
def release(options):
    """ Generate packages and upload to PyPI. """
    pass
