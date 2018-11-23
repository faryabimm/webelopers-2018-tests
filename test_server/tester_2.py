import datetime                                                                              
import requests
import time
import tests
import sys
from selenium import webdriver
for i in range(9,10):
    print("{} TEST: {}".format(datetime.datetime.now().time(), i))
    try:
        driver = webdriver.Chrome()
        test_i = getattr(tests, "test_{}".format(i))
        print(test_i("http://192.168.200.203:8000", "1", driver))
        # driver.close()
    except:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        print("test {} except".format(i))
    print(datetime.datetime.now().time())
