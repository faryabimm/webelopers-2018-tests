import time

from selenium import webdriver
import utils as ut
import random
import string

from User import User

sharif_ip = 'http://192.168.192.114:8000'
global_ip = 'http://81.31.175.72:8000'

driver = webdriver.Chrome()


def test_1(ip):
    if not ut.connect(ip, driver):
        return False
    if not check_navbar(False):
        return False

    welcome = ut.find_element_id(driver, "welcome", driver)
    if welcome.text != "به سامانه استاد جو خوش آمدید.":
        print("incorrect welcome message")
        driver.close()
        return False

    home_url = driver.current_url
    home_source = driver.page_source
    ut.find_element_id(driver, "navbar_home", driver).click()
    if driver.current_url != home_url or driver.page_source != home_source:
        print("home button doesn't work")
        driver.close()
        return False

    driver.delete_all_cookies()
    return True


def check_navbar(logged_in):
    navbar = ut.find_element_id(driver, "navbar", driver)
    if navbar is None:
        return False
    navbar_home = ut.find_element_id(navbar, "navbar_home", driver)
    if not logged_in:
        navbar_login = ut.find_element_id(navbar, "navbar_login", driver)
        navbar_signup = ut.find_element_id(navbar, "navbar_signup", driver)
        if navbar_login is None or navbar_signup is None or navbar_home is None:
            return False
    else:
        navbar_logout = ut.find_element_id(navbar, "navbar_logout", driver)
        if navbar_home is None or navbar_logout is None:
            return False
    return True


def test_2(ip, user):
    if not ut.connect(ip, driver):
        return False
    if not check_navbar(False):
        return False
    home_url = driver.current_url
    home_source = driver.page_source
    if not user.signup(driver):
        return False
    redirect_url = driver.current_url
    if driver.current_url != home_url or driver.page_source != home_source:
        print("redirect to home after signup failed")
        return False
    # todo: username password to django admin required
    username = 'mrtaalebi'
    password = '1234\',.p'
    ut.login_to_django_admin(username, password, driver, ip)
    ut.find_element_id(driver, "searchbar", driver).send_keys(user.username)
    ut.find_css_selector_element(driver, "form input[type=submit]", driver).click()
    field_username = ut.find_element_class(driver, "field-username", driver)
    if field_username is None:
        print("field_username not found in database")
        return False
    link_username = ut.find_element_tag(field_username, "a", driver)
    if link_username is None:
        print("user not found in database")
        return False
    link_username.click()
    field_first_name = ut.find_element_id(driver, "id_first_name", driver).get_attribute("value")
    field_last_name = ut.find_element_id(driver, "id_last_name", driver).get_attribute("value")
    field_email = ut.find_element_id(driver, "id_email", driver).get_attribute("value")
    if field_first_name != user.first_name or field_last_name != user.last_name or field_email != user.email:
        print("user information haven't saved correctly")
        return False

    driver.delete_all_cookies()
    return True


# user assumed to be signed up to the site
# this test is dependent to test 2 for user signup
def test_3(ip, user_1):
    if not ut.connect(ip, driver):
        return False
    if not check_navbar(False):
        return False
    if not user_1.login(driver):
        return False
    # checking right user
    if not check_navbar(True):
        return False
    driver.delete_all_cookies()
    # checking wrong user
    if not ut.connect(ip, driver):
        return False
    wrong_user = User()
    if not wrong_user.login(driver):
        return False
    if not check_navbar(False):
        return False

    driver.delete_all_cookies()
    driver.close()
    return True


user = User()
test_2("http://127.0.0.1:8000", user)
print(test_3("http://127.0.0.1:8000", user))
