import datetime                                                                              
import requests
import time
import tests
from selenium import webdriver
driver = webdriver.Chrome()
for i in range(1, 27):
    print("{} TEST: {}".format(datetime.datetime.now().time(), i))
    try:
        test_i = getattr(tests, "test_{}".format(i))
        print(test_i("http://0.0.0.0:8000", "1", driver))
        print(test_i("http://0.0.0.0:8000", "1", driver))
        driver.delete_all_cookies()
        print(test_i("http://0.0.0.0:8000", "1", driver))
        print(test_i("http://0.0.0.0:8000", "1", driver))
        print(test_i("http://0.0.0.0:8000", "1", driver))
        print(test_i("http://0.0.0.0:8000", "1", driver))
        print(test_i("http://0.0.0.0:8000", "1", driver))
        print(test_i("http://0.0.0.0:8000", "1", driver))
        print(test_i("http://0.0.0.0:8000", "1", driver))
    except:
        print("test {} except".format(i))
    print(datetime.datetime.now().time())
