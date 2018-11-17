import requests
import tests

import datetime
import utils as ut

from selenium import webdriver

print(datetime.datetime.now().time())
options = webdriver.ChromeOptions()
# options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=options)
print(tests.test_24("http://127.0.0.1:8001", "2", driver))
driver.close()


# print(ut.random_date_time())
# print(type(ut.random_date_time()))
# print(ut.random_string_not_contains(10, 'a'))

print(datetime.datetime.now().time())

#requests.post("http://0.0.0.0:6543",
#              {"group_id": "1", "ip": "http://0.0.0.0:8000", "test_order": "[1, 2, 3, 4, 7]"})
