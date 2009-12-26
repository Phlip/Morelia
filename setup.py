#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup # , find_packages

setup(name='Morelia',
      version='0.0.7',
      description='squeeze your features',
      author='Phlip',
      author_email='phlip2005@gmail.com',
      url='TODO',
      packages=['src'],
  #  packages = find_packages('src'),
    # package_dir = {'':'src'},
    keywords = "django testing bdd",
    install_requires=[],
    classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ]

     )
