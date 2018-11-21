import datetime
import tests
from selenium import webdriver
import requests

print(datetime.datetime.now().time())
options = webdriver.ChromeOptions()
#options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=options)
print(tests.test_19("http://localhost:8000", "2", driver))
# driver.close()
print(datetime.datetime.now().time())

for i in range(3, 10):
    for j in range(1, 10):
        requests.post("http://0.0.0.0:6543",
              {"group_id": j, "ip": "0.0.0.0", "port": "8000", "test_order": "{}".format(i)})

