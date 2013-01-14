
from setuptools import setup

from _version import __version__

setup(
    name                = 'yummly',
    version             = __version__,
    description         = 'Python module for Yummly API: https://developer.yummly.com',
    author              = 'Derrick Gilland',
    author_email        = 'dgilland@gmail.com',
    url                 = 'https://github.com/dgilland/yummly.py',
    license             = 'BSD',
    install_requires    = open( 'requirements.txt' ).read().split()
)

