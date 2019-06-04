import time
import requests
from athena_query import AthenaQuery
from apple_watch_3_row import AppleWatch3Row
import os


def test_transmission():
    binary_data, rows = create_payload()
    
    # Send the request
    file_number = "99"
    url = os.getenv('test_url')
    res = requests.post(url, data=binary_data, headers={"Content-Disposition": file_number})
    
    # Check response code and file number acknowledgement
    assert res.status_code == 200
    assert res.text == file_number

    # Wait for data to propagate through AWS pipeline
    time.sleep(60)
    
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


def create_payload():
    # Create the payload
    data = b""
    rows = []
    for _ in range(5 * 60 * 100):
        row = AppleWatch3Row()
        rows.append(row)
        data += row.binary_encode()
    return data, rows
