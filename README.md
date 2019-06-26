# End to end tests [![Build Status](https://travis-ci.org/kine-dmd/end-to-end-tests.svg?branch=master)](https://travis-ci.org/kine-dmd/end-to-end-tests)
These tests run daily on Travis CI to ensure the data pipeline is up and running. They write data through the API and then wait for it to be processed and stored. They use [AWS Athena](https://aws.amazon.com/athena/) to query the data and check that all of the data matches.

This repository also contains the necessary code for load testing using HT Condor.
