#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import morelia

setup(name         = 'Morelia',
      version      = morelia.__version__,
      description  = 'for "Behavior Driven Development" (BDD) -- ' +
                     'a client-facing scripting language to ' +
                     'put the squeeze on all your features',
      author       = 'Phlip',
      author_email = 'phlip2005@gmail.com',
      url          = 'http://c2.com/cgi/wiki?MoreliaViridis',
      py_modules   = ['morelia'],
      keywords     = "test bdd behavior",
      classifiers  = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        "Development Status :: 4 - Beta"
      ]
    )
