import datetime
import requests
import time

for i in range(1, 12):
    print("test {} for 40 groups started: {}".format(i, datetime.datetime.now().time()))
    for j in range(1, 40):
        requests.post("http://0.0.0.0:6543",
                {"group_id": str(j), "ip": "http://0.0.0.0:8000", "test_order": "[{}]".format(i)})
    time.sleep(60)
    print(datetime.datetime.now().time())
