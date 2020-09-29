# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Extras and utilities for Marshmallow"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.42',
    'coverage>=5.2.1',
    'pytest-cov>=2.10.1',
    'pytest-isort>=1.2.0',
    'pytest-pycodestyle>=2.2.0',
    'pytest-pydocstyle>=2.2.0',
    'pytest>=6.0',
]

extras_require = {
    'docs': [
        'Sphinx>=3.0.0',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

install_requires = [
    'arrow>=0.16.0',
    'bleach>=3.0.0',
    'edtf>=4.0.1,<5.0.0',
    'ftfy>=4.4.3',
    'marshmallow>=3.0.0,<4.0.0',
    'pycountry>=18.12.8',
    "uritemplate>=3.0.1",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('marshmallow_utils', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='marshmallow-utils',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='marshmallow utils extras',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/marshmallow-utils',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    extras_require=extras_require,
    install_requires=install_requires,
    tests_require=tests_require,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Development Status :: 5 - Production/Stable',
    ],
)
