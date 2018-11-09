import requests
import selenium.webdriver

import tests

driver = selenium.webdriver.Chrome()
print(tests.test_5("http://0.0.0.0:8000", "1", driver))

#requests.post("http://0.0.0.0:6543",
#              {"group_id": "1", "ip": "http://0.0.0.0:8000", "test_order": "[1, 2, 3, 4, 7]"})
