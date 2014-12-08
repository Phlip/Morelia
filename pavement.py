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

SUPPORTED_PLATFORMS = {
    '2.7': [
        [''],
    ],
    '3.3': [
        [''],
    ],
    '3.4': [
        [''],
    ],
}


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


def _get_venv_name(python_version, libs):
    venv = 'p%s%s' % tuple(python_version.split('.'))
    workon_home = os.environ['WORKON_HOME']
    venv = os.path.join(workon_home, venv)
    return venv


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
def prepare_venvs(options):
    venvs = []
    for python_version, lib_set in sorted(SUPPORTED_PLATFORMS.iteritems()):
        for libs in lib_set:
            venv = _get_venv_name(python_version, libs)
            venvs.append(venv)
    venvs.sort()
    options.venvs = venvs


@task
@needs('build', 'prepare_venvs')
def install_all(options):
    for venv in options.venvs:
        pip_path = '%s/bin/pip' % venv
        python_path = '%s/bin/python' % venv
        distfiles = glob.glob('dist/*')
        distfiles_num = len(distfiles)
        for idx, distfile in enumerate(distfiles):
            # install requirements
            sh('%s install -q -r requirements.txt' % pip_path)
            # uninstall old if exists
            sh('%s uninstall -q -y %s' % (pip_path, options.package_name), ignore_error=True)
            # install package
            sh('%s install -q %s' % (pip_path, distfile))
            # test package installation
            sh('%s -c "import %s"' % (python_path, options.name))
            if idx != distfiles_num - 1:
                # uninstall all but last
                sh('%s uninstall -q -y %s' % (pip_path, options.package_name), ignore_error=True)


@task
@needs('prepare_venvs', 'install_all')
def test_all(options):
    omit = ','.join([repr(filename) for filename in options.omit])
    for venv in options.venvs:
        coverage_path = '%s/bin/coverage' % venv
        # run tests
        sh('INSTALL_COVERAGE=1 %s run -p --branch --omit %s setup.py test -v' % (coverage_path, omit))


@task
@needs('test_all')
def coverage_all(options):
    sh('coverage combine')
    sh("coverage html --include='*%s*'" % options.name)
    sh("coverage report --include='*%s*' --fail-under=100" % options.name)


@task
@needs('prepare_venvs', 'install_all')
def uninstall_all(options):
    for venv in options.venvs:
        # uninstall package
        pip_path = '%s/bin/pip' % venv
        sh('%s uninstall -q -y %s' % (pip_path, options.package_name))
        sh('%s uninstall -q -y -r requirements.txt' % pip_path)


@task
@needs('cleanup', 'kwalitee', 'coverage_all', 'uninstall_all', 'html')
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


@task
def bootstrap_virtualenvs(options):
    """ Create virtualenvs for supported platforms. """
    for python_version in sorted(SUPPORTED_PLATFORMS):
        for libs in SUPPORTED_PLATFORMS[python_version]:
            venv = _get_venv_name(python_version, libs)
            sh('virtualenv -p python%s %s' % (python_version, venv))
            sh('%s/bin/pip%s install coverage' % (venv, python_version))
            lib_set = ' '.join(libs)
            if lib_set:
                sh('%s/bin/pip%s install -f ../packages %s' % (venv, python_version, lib_set))


@task
def coverage(options):
    """ Run tests and generate coverage reports. """
    omit = ','.join([repr(filename) for filename in options.omit])
    sh('coverage run --branch --source src --omit %s setup.py test' % omit)
    sh('coverage html')
    sh('coverage report')
