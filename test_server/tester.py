import datetime
import tests
from selenium import webdriver
import requests

print(datetime.datetime.now().time())
options = webdriver.ChromeOptions()
#options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=options)
# driver = webdriver.Firefox()
ip = "http://localhost:8000"
for i in range(1, 27):
    # if i not in [21]:
    #     continue
    test = getattr(tests, ('test_' + str(i)))
    print(test(ip, "2", driver))
    driver.get(ip)
    driver.delete_all_cookies()
# driver.close()
print(datetime.datetime.now().time())

# for i in range(3, 10):
#     for j in range(1, 10):
#         requests.post("http://0.0.0.0:6543",
#               {"group_id": j, "ip": "0.0.0.0", "port": "8000", "test_order": "{}".format(i)})

