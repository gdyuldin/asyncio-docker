import os
import sys

from setuptools import setup, find_packages
from distutils.sysconfig import get_python_lib

_is_setup = True
version = __import__('asyncio_docker').get_version()


setup(
    name='asyncio-docker',
    version=version,
    url='http://www.adaptiv.nl/',
    author='Raymond Reggers - Adaptiv Design',
    author_email='raymond@adaptiv.nl',
    description=('Asyncio Docker Client'),
    license='Apache Software License',
    packages=find_packages(exclude=[

    ]),
    include_package_data=True,
    install_requires=[
        'aiohttp',
        'jsonschema'
    ],
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: Apache Software License',
    ],
)
