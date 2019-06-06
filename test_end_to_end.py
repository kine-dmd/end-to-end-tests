import time
import requests
from athena_query import AthenaQuery
from apple_watch_3_row import AppleWatch3Row
from functools import reduce


def test_transmission():
    binary_data, rows = create_payload(5 * 60 * 100)
    
    # Send the request
    file_number = "99"
    url = "https://kine-dmd.co.uk/upload/apple-watch-3/00000000-0000-0000-0000-000000000000" #os.getenv('test_url')
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
    rows = [AppleWatch3Row() for _ in range (num_rows)]
    data = reduce(lambda x,y: x + y.binary_encode(), rows, b"")
    return data, rows
