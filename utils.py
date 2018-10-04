

def connect(ip, driver):
    driver.set_page_load_timeout(5)
    try:
        driver.get(ip)
    except:
        print("Connection timed out {}!".format(ip))
        driver.close()
        exit(1)

# look_in: found element
# look_for: wanted element id
def find_element(look_in, look_for, driver):
    try:
        return look_in.find_element_by_id(look_for)
    except:
        print("{} not found".format(look_for))
        driver.close()
        exit(1)

