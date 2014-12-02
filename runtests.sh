#!/bin/bash -ev

# Handy to run the right tests depending on which virtualenv you have activated
PYTHON_MAJOR=$(python --version 2>&1 | awk '{ print $2 }' | awk -F '.' '{ print $1}')
if [ $PYTHON_MAJOR -eq 3 ]; then pushd kitchen3; else pushd kitchen2; fi
$(which nosetests)
popd
