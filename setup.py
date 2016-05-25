from setuptools import setup

setup(
    name='asyncio-docker',
    version=__import__('asyncio_docker').get_version(),
    url='https://github.com/adaptivdesign/asyncio-docker',
    author='Raymond Reggers - Adaptiv Design',
    author_email='raymond@adaptiv.nl',
    description=('Asyncio Docker Client'),
    license='Apache Software License',
    packages=['asyncio_docker'],
    zip_safe=False,
    install_requires=[
        'aiohttp>=0.21.6,<0.22.0',
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
