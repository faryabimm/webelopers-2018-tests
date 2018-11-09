import utils as ut
from User import User
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ContactMessage import ContactMessage


def failed(test, message):
    return False, 'TEST {}: {}'.format(test, message)


def passed(test):
    return True, 'TEST {}: passed!'.format(test)


def test_1(ip, group_id, driver):
    msg = ''
    if not ut.connect(ip, driver, msg):
        return failed('1', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('1', msg)

    if "به سامانه استادجو خوش آمدید." not in driver.page_source:
        return failed('1', 'incorrect or not found welcome message')

    home_url = driver.current_url
    home_source = driver.page_source
    ut.find_element_id(driver, "navbar_home", msg).click()
    if driver.current_url != home_url or driver.page_source != home_source:
        return failed('1', msg)

    return passed('1')


def test_2(ip, group_id, driver):
    msg = ''
    user = User()
    if not ut.connect(ip, driver, msg):
        return failed('2', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('2', msg)
    home_url = driver.current_url
    home_source = driver.page_source
    if not user.signup(driver, msg):
        return failed('2', msg)
    if driver.current_url != home_url or driver.page_source != home_source:
        return failed('2', 'redirect to home after signup failed')
    ut.login_to_django_admin(group_id=group_id, driver=driver, ip=ip, msg=msg)
    if not ut.check_user_in_django_admin(ip, user, driver, msg):
        return failed('2', msg)

    return passed('2')


# user assumed to be signed up to the site
# this test is dependent to test 2 for user signup
def test_3(ip, group_id, driver):
    msg = ''
    if not ut.connect(ip, driver, msg):
        return failed('3', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('3', msg)
    user_1 = User()
    if not user_1.signup(driver, msg):
        return failed('3', msg)
    driver.delete_all_cookies()
    if not ut.connect(ip, driver, msg):
        return failed('3', msg)
    if not user_1.login(driver, msg):
        return failed('3', msg)
    # checking right user
    if not ut.check_navbar(True, driver, msg):
        return failed('3', msg)
    login_error_message = "نام کاربری یا گذرواژه غلط است"
    if login_error_message in driver.page_source:
        return failed('3', 'no login message error shown')
    driver.delete_all_cookies()
    # checking wrong user
    if not ut.connect(ip, driver, msg):
        return failed('3', msg)
    wrong_user = User()
    if not wrong_user.login(driver, msg):
        return failed('3', msg)
    if login_error_message not in driver.page_source:
        return failed('3', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('3', msg)

    return passed('3')


def test_4(ip, group_id, driver):
    msg = ''
    if not ut.connect(ip, driver, msg):
        return failed('4', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('4', msg)
    user_exists = "کاربری با نام کاربری وارد شده وجود دارد"
    email_exists = "کاربری با ایمیل وارد شده وجود دارد"
    password_mismatch = "گذرواژه و تکرار گذرواژه یکسان نیستند"

    error_msg = 'wrong errors'

    # all correct
    user_1 = User()
    if not user_1.signup(driver, msg):
        return failed('4', msg)
    print("if1")
    source_1 = driver.page_source
    if user_exists in source_1 or password_mismatch in source_1 or email_exists in source_1:
        return failed('4', error_msg)
    print("if2")
    driver.delete_all_cookies()

    # username error
    user_2 = User()
    user_2.username = user_1.username
    user_2.signup(driver, msg)
    source_2 = driver.page_source
    if user_exists not in source_2 or password_mismatch in source_2 or email_exists in source_2:
        return failed('4', error_msg)
    print("if3")
    driver.delete_all_cookies()

    # email error
    user_3 = User()
    user_3.email = user_1.email
    user_3.signup(driver, msg)
    source_3 = driver.page_source
    if user_exists in source_3 or password_mismatch in source_3 or email_exists not in source_3:
        return failed('4', error_msg)
    print("if4")
    driver.delete_all_cookies()

    # password mismatch error
    user_4 = User()
    user_4.signup(driver, msg, send_mismatched_password=True)
    source_4 = driver.page_source
    if user_exists in source_4 or password_mismatch not in source_4 or email_exists in source_4:
        return failed('4', error_msg)
    print("if5")
    ut.login_to_django_admin(group_id=group_id, driver=driver, ip=ip, msg=msg)
    if not ut.check_user_in_django_admin(ip, user_1, driver, msg):
        return failed('4', msg)
    print("if6")
    if ut.check_user_in_django_admin(ip, user_2, driver, msg):
        return failed('4', msg)
    print("if7")
    if ut.check_user_in_django_admin(ip, user_3, driver, msg):
        return failed('4', msg)
    print("if8")
    if ut.check_user_in_django_admin(ip, user_4, driver, msg):
        return failed('4', msg)
    print("if9")
    return passed('4')


def test_5(ip, group_id, driver):
    msg = ''
    if not ut.connect(ip, driver, msg):
        return failed('5', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('5', msg)
    navbar = ut.find_element_id(driver, "navbar", msg)
    if navbar is None:
        return failed('5', msg)
    contact_us = ut.find_element_id(navbar, "navbar_contact_us", msg)
    if contact_us is None:
        return failed('5', msg)
    contact_us.click()
    title_field = ut.find_element_id(driver, "id_title", msg)
    email_field = ut.find_element_id(driver, "id_email", msg)
    text_field = ut.find_element_id(driver, "id_text", msg)
    submit_button = ut.find_element_id(driver, "signup_submit", msg)
    if title_field is None or email_field is None or text_field is None or submit_button is None:
        return failed('5', msg)
    if title_field.get_attribute("maxlength") != "40":
        return failed('5', "title field maxlength")
    if email_field.get_attribute("type") != "email":
        return failed('5', "email field type")
    if text_field.get_attribute("minlength") != "10" or text_field.get_attribute("maxlength") != "250":
        return failed('5', "text field min or max length")
    message = ContactMessage()
    title_field.send_keys(message.title)
    email_field.send_keys(message.email)
    text_field.send_keys(message.text)
    submit_button.click()
    # TODO: TOO SLOW AND BLOCKING
    submitted = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.XPATH, "//*"), "درخواست شما ثبت شد"))
    if submitted is None:
        return failed('5', "sending email took too long time")
    return passed('5')


def test_6(ip, gruop_id, driver):

    return False, 'PASS', 'PASS'


def test_7(ip, group_id, driver):
    msg = ''
    if not ut.connect(ip, driver, msg):
        return failed('7', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('7', msg)
    if ut.find_element_id(driver, "navbar", msg) is None:
        return failed('7', msg)
    user_1 = User()
    if not user_1.signup(driver, msg):
        return failed('7', msg)
    if not user_1.login(driver, msg):
        return failed('7', msg)
    if not ut.check_navbar(True, driver, msg):
        return failed('7', msg)
    user_1.logout(driver, msg)
    if "به سامانه استادجو خوش آمدید." not in driver.page_source:
        return failed('7', 'incorrect or not found welcome message')
    if not ut.check_navbar(False, driver, msg):
        return failed('7', msg)
    return passed('7')
