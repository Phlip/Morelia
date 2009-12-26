#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup # , find_packages

setup(name='Morelia',
      version='0.0.1',
      description='put the squeeze on your features',
      author='Phlip',
      author_email='phlip2005@gmail.com',
      url='TODO',

      py_modules=['morelia'],
  #  packages = find_packages('src'),
    #package_dir = {'':'morelia'},
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
