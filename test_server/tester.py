import datetime
import tests
from selenium import webdriver

print(datetime.datetime.now().time())
options = webdriver.ChromeOptions()
#options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=options)
print(tests.test_11("http://127.0.0.1:8000", "1", driver))
print(datetime.datetime.now().time())

#requests.post("http://0.0.0.0:6543",
#              {"group_id": "1", "ip": "http://0.0.0.0:8000", "test_order": "[1, 2, 3, 4, 7]"})
