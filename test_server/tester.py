import requests

requests.post("http://0.0.0.0:6543",
              {"group_id": 1, "ip": "http://0.0.0.0:8000", "test_order": "[1, 2, 3, 4, 5, 6, 7]"})
