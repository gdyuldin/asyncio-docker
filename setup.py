from setuptools import setup, find_packages

setup(
    name='asyncio-docker2',
    version=__import__('asyncio_docker').get_version(),
    url='https://github.com/adaptivdesign/asyncio-docker',
    author='Georgy Dyuldin (Fork author)',
    author_email='g.dyuldin@gmail.com',
    description=('Asyncio Docker Client (Fork)'),
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
