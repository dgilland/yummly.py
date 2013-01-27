#!/usr/bin/env python

# write current version to file
execfile('yummly/version.py')
with open('VERSION', 'wb') as f:
    f.write( __version__ )
