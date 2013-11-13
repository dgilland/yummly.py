
from setuptools import setup

with open('VERSION', 'r') as f:
    version = f.read()

with open('README', 'r') as f:
    long_description = f.read()

setup(
    name                = 'yummly',
    version             = version,
    description         = 'Python package for Yummly API: https://developer.yummly.com',
    long_description    = long_description,
    author              = 'Derrick Gilland',
    author_email        = 'dgilland@gmail.com',
    url                 = 'https://github.com/dgilland/yummly.py',
    packages            = [ 'yummly' ],
    install_requires    = ['requests>=1.1.0'],
    keywords            = 'yummly recipes',
    license             = 'BSD',
    classifiers         = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License'
    ]
)

