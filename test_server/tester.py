import datetime
import tests
from selenium import webdriver
import requests


for i in range(3, 4):
    for j in range(1, 10):
        requests.post("http://0.0.0.0:6543",
              {"group_id": j, "ip": "0.0.0.0", "port": "8000", "test_order": "{}".format(i)})
    
