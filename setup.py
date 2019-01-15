#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    # TODO: put package requirements here
    'mock',
    'parse',
    'six',
]

setup(
    name='Morelia',
    version='0.7.1',
    description='for "Behavior Driven Development" (BDD) -- a client-facing scripting language to put the squeeze on all your features',
    long_description=readme,
    author='Morelia authors',
    author_email='jakub.stolarski@gmail.com',
    url='https://github.com/kidosoft/morelia',
    packages=find_packages(exclude=['tests']),
    package_dir={'morelia':
                 'morelia'},
    include_package_data=True,
    install_requires=requirements,
    license='MIT license',
    zip_safe=False,
    keywords='test bdd behavior',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        ':python_version=="2.7"': ['mock'],
    },
)
