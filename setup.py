from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='Morelia',
    version='0.6.5',
    description='for "Behavior Driven Development" (BDD) -- a client-facing scripting language to put the squeeze on all your features',
    long_description=long_description,
    url='http://morelia.readthedocs.org/',
    author='Phlip, Jakub STOLARSKI (Dryobates)',
    author_email='phlip2005@gmail.com, jakub.stolarski@kidosoft.pl',
    license='MIT',
    keywords='test bdd behavior',
    packages=find_packages('src'),  # , exclude=['example*', '*.tests', 'tests.*', '*.tests.*', 'tests']),
    package_dir={'': 'src'},
    install_requires=[
        'six',
        'parse',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite="morelia.tests",
)
