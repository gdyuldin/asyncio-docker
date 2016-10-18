from setuptools import setup, find_packages

setup(
    name='asyncio-docker',
    version=__import__('asyncio_docker').get_version(),
    url='https://github.com/adaptivdesign/asyncio-docker',
    author='Raymond Reggers - Adaptiv Design',
    author_email='raymond@adaptiv.nl',
    description=('Asyncio Docker Client'),
    license='Apache Software License',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'aiohttp>=1.0.0,<1.1.0',
        'jsonschema>=2.5.1,<2.6.0'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: Apache Software License',
    ],
)
