#!/usr/bin/env bash
set -e

# Activate the venv
source venv/bin/activate

# Run the load test script
python3 load_test.py send
