#!/usr/bin/env python
"""
$Id$
see http://peak.telecommunity.com/DevCenter/setuptools

note: if you want to develop this code and run from code on the command line,
please run the following line when you update to a new version of the code.

python setup.py develop --install-dir=$HOME/Library/Python

distribution:
python setup.py develop --install-dir=$HOME/Library/Python
python setup.py sdist
python setup.py bdist_egg
"""

# changed to support egg distribution
from setuptools import setup, find_packages

setup( name="geocat_converter",
       version="0.1",
       zip_safe = True,
       entry_points = { 'console_scripts': [ 'geocat_converter = convert:main' ] },
       packages = find_packages('.'),
       install_requires=[ 'netCDF4', 'pyhdf' ],
       package_data = {'': [ ]}
       )

