from setuptools import setup, find_packages

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='Morelia',
    version="0.4.1",
    description='for "Behavior Driven Development" (BDD) -- a client-facing scripting language to put the squeeze on all your features',
    long_description=long_description,
    url='http://morelia.readthedocs.org/',
    author='Phlip',
    author_email='phlip2005@gmail.com',
    license="MIT",
    keywords="test bdd behavior",
    packages=find_packages('src', exclude=['example*']),
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
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
    test_suite="morelia.tests",
)
