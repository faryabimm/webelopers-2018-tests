import random
import string

import utils as ut


def connect(ip, driver):
    try:
        driver.get(ip)
        return True
    except:
        print("Connection timed out {}!".format(ip))
        driver.close()
        return False


# look_in: found element
# look_for: wanted element id
def find_element_id(look_in, look_for, driver):
    try:
        return look_in.find_element_by_id(look_for)
    except:
        print("{} not found".format(look_for))
        driver.close()
        return None


def find_element_class(look_in, look_for, driver):
    try:
        return look_in.find_element_by_class_name(look_for)
    except:
        print("{} not found".format(look_for))
        driver.close()
        return None


def find_element_tag(look_in, look_for, driver):
    try:
        return look_in.find_element_by_tag_name(look_for)
    except:
        print("{} not found".format(look_for))
        driver.close()
        return None


def find_element_name(look_in, look_for, driver):
    try:
        return look_in.find_element_by_name(look_for)
    except:
        print("{} not found".format(look_for))
        driver.close()
        return None


def find_css_selector_element(look_in, css_selector, driver):
    try:
        return look_in.find_element_by_css_selector(css_selector)
    except:
        print("{} not found".format(css_selector))
        driver.close()
        return None


def fill_field(field, text, driver):
    try:
        field.send_keys(text)
        return True
    except:
        print("{} not filled".format(field.get_attribute("id")))
        return False


def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def random_email():
    return "{}@{}.{}".format(random_string(random.randint(5,9)),
                             random_string(random.randint(4,7)),
                             random_string(random.randint(3,4)))


def login_to_django_admin(username, password, driver, ip):
    driver.get(ip + "/admin/auth/user/")
    ut.find_element_name(driver, "username", driver).send_keys(username)
    ut.find_element_name(driver, "password", driver).send_keys(password)
    ut.find_css_selector_element(driver, "form input[type=submit]", driver).click()
