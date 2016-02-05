import os
import sys

from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib

_is_setup = True
version = __import__('aiodocker').get_version()

EXCLUDE_FROM_PACKAGES = [

]

setup(
    name='aiodocker',
    version=version,
    url='http://www.adaptiv.nl/',
    author='Raymond Reggers - Adaptiv Design',
    author_email='raymond@adaptiv.nl',
    description=('AsyncIO Docker Client'),
    license='BSD',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    install_requires=[
        'aiohttp',
        'jsonschema',
        'attrdict'
    ],
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ], )
