#!/bin/bash

# This is a script to document the commands used to check, test, and build this
#   package.

printf "*********************************************************************\n"
printf "Run pylint to check for common code convention warnings\n"
pylint *

printf "*********************************************************************\n"
printf "Run the unit test for all subdirectories\n"
python3 -m unittest discover

