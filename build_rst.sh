#!/bin/bash

pandoc -s README.md -t rst -o README
pandoc -s CHANGES.md -t rst -o CHANGES
