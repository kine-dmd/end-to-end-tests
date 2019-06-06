#!/usr/bin/env bash
set -e

# Remove any old documents that may be present
rm -rf /tmp/rp1615

# Make a virtual environment specific to this PC
python3 -m venv /tmp/rp1615/venv

# Activate the venv
source /tmp/rp1615/venv/bin/activate

# Install dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Run the load test script
python3 load_test.py send
