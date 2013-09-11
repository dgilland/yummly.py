
from setuptools import setup

setup(
    name                = 'yummly',
    version             = open( 'VERSION' ).read(),
    description         = 'Python package for Yummly API: https://developer.yummly.com',
    long_description    = open( 'README' ).read(),
    author              = 'Derrick Gilland',
    author_email        = 'dgilland@gmail.com',
    url                 = 'https://github.com/dgilland/yummly.py',
    packages            = [ 'yummly' ],
    install_requires    = open( 'requirements.txt' ).read().split(),
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

