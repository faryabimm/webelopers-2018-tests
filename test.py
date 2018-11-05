import datetime
import time

from selenium import webdriver
import utils as ut

from User import User

sharif_ip = 'http://192.168.192.114:8000'
global_ip = 'http://81.31.175.72:8000'

driver = webdriver.Chrome()


def test_1(ip):
    if not ut.connect(ip, driver):
        return False
    if not check_navbar(False):
        return False

    if "به سامانه استادجو خوش آمدید." not in driver.page_source:
        print("incorrect or not found welcome message")
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


def test_2(ip, driver):
    user = User()
    if not ut.connect(ip, driver):
        return False
    if not check_navbar(False):
        return False
    home_url = driver.current_url
    home_source = driver.page_source
    if not user.signup(driver):
        return False
    if driver.current_url != home_url or driver.page_source != home_source:
        print("redirect to home after signup failed")
        return False

    ut.login_to_django_admin(username='mrtaalebi', password='1234\',.p', driver=driver, ip=ip)
    if not ut.check_user_in_django_admin(ip, user, driver):
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
    login_error_message = "نام کاربری یا گذرواژه غلط است"
    if login_error_message in driver.page_source:
        return False
    driver.delete_all_cookies()
    # checking wrong user
    if not ut.connect(ip, driver):
        return False
    wrong_user = User()
    if not wrong_user.login(driver):
        return False
    if login_error_message not in driver.page_source:
        return False
    if not check_navbar(False):
        return False

    driver.delete_all_cookies()
    return True


def test_4(ip):
    if not ut.connect(ip, driver):
        return False
    if not check_navbar(False):
        return False
    user_exists = "کاربری با نام کاربری وارد شده وجود دارد"
    email_exists = "کاربری با ایمیل وارد شده وجود دارد"
    password_mismatch = "گذرواژه و تکرار گذرواژه یکسان نیستند"

    # all correct
    user_1 = User()
    if not user_1.signup(driver):
        return False
    source_1 = driver.page_source
    if user_exists in source_1 or password_mismatch in source_1 or email_exists in source_1:
        return False
    driver.delete_all_cookies()

    # username error
    user_2 = User()
    user_2.username = user_1.username
    user_2.signup(driver)
    source_2 = driver.page_source
    if user_exists not in source_2 or password_mismatch in source_2 or email_exists in source_2:
        return False
    driver.delete_all_cookies()

    # email error
    user_3 = User()
    user_3.email = user_1.email
    user_3.signup(driver)
    source_3 = driver.page_source
    if user_exists in source_3 or password_mismatch in source_3 or email_exists not in source_3:
        return False
    driver.delete_all_cookies()

    # password mismatch error
    user_4 = User()
    user_4.signup(driver, send_mismatched_password=True)
    source_4 = driver.page_source
    if user_exists in source_4 or password_mismatch not in source_4 or email_exists in source_4:
        return False
    driver.delete_all_cookies()

    ut.login_to_django_admin(username='mrtaalebi', password='1234\',.p', driver=driver, ip=ip)
    if not ut.check_user_in_django_admin(ip, user_1, driver):
        return False
    print("1")
    if ut.check_user_in_django_admin(ip, user_2, driver):
        return False
    print("2")
    if ut.check_user_in_django_admin(ip, user_3, driver):
        return False
    print("3")
    if ut.check_user_in_django_admin(ip, user_4, driver):
        return False
    print("4")
    return True


def test_5(ip, driver):
    if not ut.connect(ip, driver):
        return False
    if not check_navbar(False):
        return False


def test_7(ip, driver):
    if not ut.connect(ip, driver):
        return False
    if not check_navbar(False):
        return False
    navbar = ut.find_element_id(driver, "navbar", driver)
    if navbar is None:
        return False
    user_1 = User()
    if not user_1.signup(driver):
        print("during test_7 signup failed")
        return False
    if not user_1.login(driver):
        print("during test_7 login failed")
        return False
    if not check_navbar(True):
        return False
    user_1.logout(driver)
    if "به سامانه استادجو خوش آمدید." not in driver.page_source:
        print("incorrect or not found welcome message")
        return False
    if not check_navbar(False):
        return False
    return True


print(datetime.datetime.now())
print(test_7("http://127.0.0.1:8000", driver))
print(datetime.datetime.now())
