import time
import requests
from athena_query import AthenaQuery
from apple_watch_3_row import AppleWatch3Row
import os

def test_transmission():
    # Create one hour of data
    binary_data, rows = create_payload(60 * 60 * 100)
    
    # Send the request
    file_number = "99"
    url = os.getenv('test_url')
    res = requests.post(url, data=binary_data, headers={"Content-Disposition": file_number})
    
    # Check response code and file number acknowledgement
    assert res.status_code == 200
    assert res.text == file_number

    # Wait for data to propagate through AWS pipeline
    time.sleep(30)
    
    # Query the recently added data
    query = AthenaQuery("eu-west-2")
    query.send_query("mydatabase", "SELECT * FROM daily_test WHERE ts >= {} ORDER BY ts ASC".format(rows[0].ts))
    result = query.wait_for_result()
    
    # Check that retrieved data is the same as the sent data
    assert len(result) == len(rows)
    for i in range(len(result)):
        assert rows[i] == result[i]
    
    # Delete the CSV results file
    query.cleanup_local_file()


def create_payload(num_rows):
    # Make the rows and append the binary data together
    rows = [AppleWatch3Row() for _ in range(num_rows)]
    data = b"".join([row.binary_encode() for row in rows])
    return data, rows
