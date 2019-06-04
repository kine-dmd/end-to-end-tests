#!/usr/bin/env bash

set -e

# Delete an old virtual environment if it exists
rm -rf /data/loadTestVenv

# Make a new venv
virtualenv -p /usr/bin/python3 /data/loadTestVenv

# Activate the venv
source /data/loadTestVenv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Run the load test script
python3 load_test.py send
