#!/bin/bash

# This is supposed to run in the context of a docker container that is
# created by start_docker_tests.sh.

echo "##### Installing the requirements #########"
pip install -r /work/requirements.txt

echo "##### Installing steinlib dev #############"
(cd /work && python setup.py develop)

echo "##### Running the tests ###################"
(cd /work && nose2)
