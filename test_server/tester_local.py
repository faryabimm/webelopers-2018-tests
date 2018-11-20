import datetime                                                                              
import requests
import time
import tests
from selenium import webdriver
driver = webdriver.Chrome()

print(datetime.datetime.now().time())
print(tests.test_1("http://0.0.0.0:8000", "1", driver))
print(datetime.datetime.now().time())
