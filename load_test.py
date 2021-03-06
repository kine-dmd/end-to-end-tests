import requests
from test_end_to_end import create_payload
import logging
import random
import boto3
import string
import sys

# Warning message when adding and removing uuids from the DB
PROPAGATION_WARNING = "Note this may take up to 2 hours to propagate to all instances."

def generate_test_uuids():
    return ["00000000-0000-0000-0000-000000001{:03d}".format(i) for i in range(300)]


def connect_to_uuid_db():
    dynamo_db = boto3.resource('dynamodb')
    return dynamo_db.Table('apple_watch_3_positions')

def send_requests():
    """
    Infinitely send requests to the server to test load capacity
    :return: Never terminates
    """
    # Read in the list of test UUIDs from a CSV file
    uuids = generate_test_uuids()

    # Create a binary payload of 1 hour's data (just once for speed)
    print("Beginning data generation")
    binary_data, _ = create_payload(60 * 60 * 100)
    
    # Repeat until process is terminated
    print("Beginning transmissions")
    while True:
        # Send the request
        uuid = random.choice(uuids)
        url = "https://kine-dmd.co.uk/upload/apple-watch-3/" + uuid
        res = requests.post(url, data=binary_data)
        
        # Log an error if one occurs
        if res.status_code == 200:
            print("Successfully sent {}".format(uuid))
        else:
            logging.error("Received status code {}. {}".format(res.status_code, res.text))


def add_uuids_to_db():
    """
    Add test uuids to dynamoDB. This needs to be done 2 hours in advance of a planned load test.
    :return:
    """
    # Connect to the table in DynamoDB)
    uuid_db =  connect_to_uuid_db()

    # Write data in batches of 10
    uuids = generate_test_uuids()
    for i in range(0, len(uuids), 10):
        uuid_subset = uuids[i: i + 10]
    
        # Add all of the test rows in the database
        with uuid_db.batch_writer(overwrite_by_pkeys=['uuid']) as batch_writer:
            for uuid in uuid_subset:
                row = {'uuid': uuid,
                       'patientId': ''.join(random.choice(string.ascii_letters) for _ in range(5)),
                       'limb': random.choice(range(4))}
                
                batch_writer.put_item(Item=row)
    
    print("Adding UUIDs complete. {}".format(PROPAGATION_WARNING))


def delete_uuids_from_db():
    # Connect to the table in DynamoDB
    uuid_db = connect_to_uuid_db()
    
    # Write data in batches of 10
    uuids = generate_test_uuids()
    for i in range(0, len(uuids), 10):
        uuid_subset = uuids[i: i+10]
    
        # Delete all of the test rows in the database
        with uuid_db.batch_writer(overwrite_by_pkeys=['uuid']) as batch_writer:
            for uuid in uuid_subset:
                batch_writer.delete_item(
                    Key={
                        'uuid': uuid
                    }
                )

    print("Deleting UUIDs complete. {}".format(PROPAGATION_WARNING))

            
def pick_option():
    # Error message when no argument provided
    error_msg = "Please provide a single line argument for your intended use. Either 'send', 'add', or 'delete'."
    
    # Check a command line argument has been provided
    if len(sys.argv) != 2:
        print(error_msg)
        
    # Invoke the appropriate function depending on use case
    if sys.argv[1] == 'send':
        send_requests()
    elif sys.argv[1] == 'add':
        add_uuids_to_db()
    elif sys.argv[1] == 'delete':
        delete_uuids_from_db()
    else:
        print(error_msg)



### Main ###
pick_option()