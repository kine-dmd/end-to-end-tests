import csv
import random

import boto3
import time
import os


class AthenaQuery(object):
    """
    The Athena Query object allows you to submit a query to AWS Athena, and then later on wait for the result.
    Designed to work for a single query per object that returns numeric only data.
    """
    
    def __init__(self, region):
        """
        Make a query object in a given AWS region
        :param region: The AWS region the table is in
        """
        session = boto3.Session()
        self.athena_client = session.client('athena', region_name=region)
        self.s3_client = boto3.client('s3')
        self.execution_id = None
        self.local_location = None


    def send_query(self,
                   database,
                   query,
                   output_bucket="aws-athena-query-results-736634562271-eu-west-2",
                   output_folder="unsaved"):
        """
        Start running a query on AWS Athena. Does not block waiting for query to finish.
        :param database: The database on Athena you wish to query
        :param query: The SQL query itself
        :param output_bucket: S3 bucket that output should be written to (optional)
        :param output_folder: S3 Bucket output folder (optional)
        :return:
        """
        response = self.athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': 's3://' + output_bucket + '/' + output_folder
            }
        )
        self.execution_id = response['QueryExecutionId']


    def wait_for_result(self):
        # If not already downloaded result
        if self.local_location is None:
            
            #Find the location of the file on S3
            s3_loc = self.get_s3_location()
            if s3_loc is None:
                return None
        
            # Download the file
            self.local_location = "results-{}.csv".format(random.randint(0, 10**10))
            with open(self.local_location, 'wb') as f:
                # Remove s3:// prefix and split bucket name from path
                s3_bucket, s3_path = s3_loc[5:].split('/', 1)
                self.s3_client.download_fileobj(s3_bucket, s3_path, f)
            
        return AthenaQuery.parse_csv_file(self.local_location)
        
        

    def get_s3_location(self):
        # Initial constraints
        state = 'RUNNING'
        attempts = 0
        
        # Try checking the status up to 100 times
        while attempts < 100 and state == 'RUNNING':
            # Get the current query status ('QUEUED'|'RUNNING'|'SUCCEEDED'|'FAILED'|'CANCELLED')
            response = self.athena_client.get_query_execution(QueryExecutionId=self.execution_id)
            attempts += 1
        
            state = response['QueryExecution']['Status']['State']
            if state == 'FAILED':
                return None
            elif state == 'SUCCEEDED':
                return response['QueryExecution']['ResultConfiguration']['OutputLocation']
        
            # Wait before re-asking for result
            time.sleep(10)
        
        # If timed out
        return None



    def cleanup_local_file(self):
        if self.local_location is not None:
            os.remove(self.local_location)

    @staticmethod
    def parse_csv_file(filename):
        """
        Parses a numeric only CSV file as downloaded from Athena outputs
        :param filename: Location of the CSV file
        :return: [tuple] List of rows
        """
        with open(filename, newline='\n') as csvfile:
            
            # Read the file and skip the first line
            csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csv_reader)
            
            # Read all subsequent rows
            all_rows = []
            for row in csv_reader:
                # Convert the row from string to numbers
                row = tuple(map(float, row))
                all_rows.append(row)
        
            return all_rows
        

