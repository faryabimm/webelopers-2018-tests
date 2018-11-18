import filecmp
import os
import urllib.request

import utils as ut
from PIL import Image, ImageChops
from User import User
from Event import Event
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ContactMessage import ContactMessage

import random
import json


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


def submit_contact_us(ip, group_id, driver, msg):
    if not ut.connect(ip, driver, msg):
        return None
    if not ut.check_navbar(False, driver, msg):
        return None
    navbar = ut.find_element_id(driver, "navbar", msg)
    if navbar is None:
        return None
    contact_us = ut.find_element_id(navbar, "navbar_contact_us", msg)
    if contact_us is None:
        return None
    contact_us.click()
    title_field = ut.find_element_id(driver, "id_title", msg)
    email_field = ut.find_element_id(driver, "id_email", msg)
    text_field = ut.find_element_id(driver, "id_text", msg)
    submit_button = ut.find_element_id(driver, "signup_submit", msg)
    if title_field is None or email_field is None or text_field is None or submit_button is None:
        return None
    if title_field.get_attribute("maxlength") != "40":
        msg += "title field maxlength"
        return None
    if email_field.get_attribute("type") != "email":
        msg += "email field type"
        return None
    if text_field.get_attribute("minlength") != "10" or text_field.get_attribute("maxlength") != "250":
        msg += "text field min or max length"
        return None
    message = ContactMessage()
    title_field.send_keys(message.title)
    email_field.send_keys(message.email)
    text_field.send_keys(message.text)
    submit_button.click()
    return message


def test_5(ip, group_id, driver):
    msg = ''
    # TODO: TOO SLOW AND BLOCKING
    message = submit_contact_us(ip, group_id, driver, msg)
    if message is None:
        return failed('5', msg)
    submitted = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.XPATH, "//*"), "درخواست شما ثبت شد"))
    if submitted is None:
        return failed('5', "sending email took too long time")
    return passed('5')


def test_6(ip, group_id, driver):
    msg = ''
    message = submit_contact_us(ip, group_id, driver, msg)
    if message is None:
        return failed('6', msg)
    if not ut.connect("https://www.fastmail.com/login/", driver, msg):
        return failed('6', msg)
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.XPATH, "//*"), "Log In"))
    username_field = ut.find_element_name(driver, "username", msg)
    password_field = ut.find_element_name(driver, "password", msg)
    login_button = ut.find_css_selector_element(driver, "button", msg)
    if username_field is None or password_field is None or login_button is None:
        return failed('6', msg)
    username_field.send_keys("ostadju@fastmail.com")
    password_field.send_keys("thegreatramz")
    login_button.click()
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.XPATH, "//*"), "No Conversation Selected"))
    title_link = ut.find_css_selector_element(driver, "div[title={}]".format(message.title), msg)
    if title_link is None:
        return failed('6', msg)
    title_link.click()
    WebDriverWait(driver, 5).until(
        EC.text_to_be_present_in_element((By.XPATH, "//*"), "Reply"))
    source = driver.page_source
    if message.text not in source or message.email not in source:
        return failed('6', "contact us message hasn't sent correctly")
    return passed('6')


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


def create_user_goto_profile(ip, group_id, driver, msg):
    if not ut.connect(ip, driver, msg):
        return None
    if not ut.check_navbar(False, driver, msg):
        return None
    navbar = ut.find_element_id(driver, "navbar", msg)
    if navbar is None:
        return None
    profile = ut.find_element_id(navbar, "navbar_profile", msg)
    if profile is not None:
        msg += "profile link on navbar before login"
        return None
    user_1 = User()
    if not user_1.signup(driver, msg):
        return None
    if not user_1.login(driver, msg):
        return None
    profile = ut.find_element_id(navbar, "navbar_profile", msg)
    if profile is None:
        return None
    profile.click()
    return user_1


def test_8(ip, group_id, driver):
    msg = ''
    user_1 = create_user_goto_profile(ip, group_id, driver, msg)
    if user_1 is None:
        return failed('8', msg)
    source = driver.page_source
    if user_1.first_name not in source or user_1.last_name not in source or user_1.username not in source:
        return failed('8', "incorrect user profile information")
    return passed('8')


def test_9(ip, group_id, driver):
    msg = ''
    user_1 = create_user_goto_profile(ip, group_id, driver, msg)
    if user_1 is None:
        return failed('9', msg)
    edit_profile = ut.find_element_id(driver, "edit_profile", msg)
    if edit_profile is None:
        return failed('9', msg)
    edit_profile.click()
    field_first_name = ut.find_element_id(driver, "id_first_name", msg)
    field_last_name = ut.find_element_id(driver, "id_last_name", msg)
    submit_button = ut.find_css_selector_element(driver, "input[type=submit]", msg)
    if field_first_name is None or field_last_name is None or submit_button is None:
        return failed('9', msg)
    first_name_salt = ut.random_string(5)
    last_name_salt = ut.random_string(5)
    field_first_name.send_keys(first_name_salt)
    field_last_name.send_keys(last_name_salt)
    submit_button.click()
    field_first_name = ut.find_element_id(driver, "text_firstname", msg)
    field_last_name = ut.find_element_id(driver, "text_lastname", msg)
    if field_first_name is None or field_last_name is None:
        return failed('9', msg)
    edited_first_name = user_1.first_name + first_name_salt
    edited_last_name = user_1.last_name + last_name_salt
    if edited_first_name not in field_first_name.text or edited_last_name not in field_last_name.text:
        return failed('9', "data hasn't edited properly")
    return passed('9')


def test_10(ip, group_id, driver):
    msg = ''
    user_1 = create_user_goto_profile(ip, group_id, driver, msg)
    if user_1 is None:
        return failed('10', msg)
    edit_profile = ut.find_element_id(driver, "edit_profile", msg)
    if edit_profile is None:
        return failed('9', msg)
    edit_profile.click()
    bio_field = ut.find_element_id(driver, "id_bio", msg)
    # FIXME this gender_select heavily depends on site's model and may fail
    gender_select = ut.find_element_id(driver, "id_gender", msg)
    gender_option = {}
    gender_option['M'] = ut.find_css_selector_element(driver, "option[value=M]", msg)
    gender_option['F'] = ut.find_css_selector_element(driver, "option[value=F]", msg)
    submit = ut.find_css_selector_element(driver, "input[type=submit]", msg)
    if bio_field is None or gender_select is None or submit is None \
            or gender_option['M'] is None or gender_option['F'] is None:
        return failed('10', msg)
    user_1.bio = ut.random_string(200)
    bio_field.send_keys(user_1.bio)
    user_1.gender = random.choice(['M', 'F'])
    gender_option[user_1.gender].click()
    submit.click()
    if user_1.bio not in driver.page_source:
        return failed('10', "user bio has not been saved")
    text_gender = ut.find_element_id(driver, "text_gender", msg)
    if text_gender is None:
        return failed('10')
    gender = {'M': "مرد", 'F': "زن"}
    if gender[user_1.gender] not in text_gender.text:
        return failed('10', "user gender has not been saved correctly")
    return passed('10')


def test_11(ip, group_id, driver):
    msg = ''
    user_1 = create_user_goto_profile(ip, group_id, driver, msg)
    if user_1 is None:
        return failed('11', msg)
    edit_profile = ut.find_element_id(driver, "edit_profile", msg)
    if edit_profile is None:
        return failed('11', msg)
    edit_profile.click()
    pic_upload = ut.find_element_id(driver, "id_picture", msg)
    submit = ut.find_css_selector_element(driver, "input[type=submit]", msg)
    if pic_upload is None or submit is None:
        return failed('11', msg)
    path = os.path.abspath("../static/{}.jpeg".format(random.randint(1,3)))
    pic_upload.send_keys(path)
    user_1.profile_image = Image.open(path)
    submit.click()
    profile_pic = ut.find_element_id(driver, "profile_image", msg)
    if profile_pic is None:
        return failed('11', msg)
    src = profile_pic.get_attribute('src')
    urllib.request.urlretrieve(src, "temp.png")
    uploaded = Image.open(os.path.abspath("temp.png"))
    pixelsDifference = ImageChops.difference(user_1.profile_image, uploaded).convert('L')
    pixelsDifference = pixelsDifference.point(([0] + ([255] * 255)))
    Img = pixelsDifference.convert('RGB')
    return passed('11')


def prepare_search(driver, query, test_num, msg):
    correct_list = []
    wrong_list = []

    for i in range(20):
        user = User([True, False])
        state = random.randint(0, 3)
        if state == 0:
            user.username = ut.random_string_contains(10, query)
            user.first_name = ut.random_string_not_contains(10, query)
            user.last_name = ut.random_string_not_contains(10, query)
        if state == 1:
            user.username = ut.random_string_not_contains(10, query)
            user.first_name = ut.random_string_contains(10, query)
            user.last_name = ut.random_string_not_contains(10, query)
        if state == 2:
            user.username = ut.random_string_not_contains(10, query)
            user.first_name = ut.random_string_not_contains(10, query)
            user.last_name = ut.random_string_contains(10, query)
        if state == 3:
            user.username = ut.random_string_not_contains(10, query)
            user.first_name = ut.random_string_not_contains(10, query)
            user.last_name = ut.random_string_not_contains(10, query)
        if user.is_student:
            wrong_list.append(user)
        elif state == 3:
            wrong_list.append(user)
        else:
            correct_list.append(user)
        if not user.signup(driver, msg, send_type=True):
            return failed(test_num, msg)

    return correct_list, wrong_list


def test_13(ip, group_id, driver):
    msg = ''
    if not ut.connect(ip, driver, msg):
        return failed('13', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('13', msg)

    query = ut.random_string(random.randint(3, 7))
    # print(query)

    correct_list, wrong_list = prepare_search(driver, query, '13', msg)

    search_box = ut.find_css_selector_element(driver, 'input#search_profiles', msg)
    search_button = ut.find_css_selector_element(driver, 'button#search_profiles', msg)
    if search_box is None or search_button is None:
        return failed('13', msg)
    search_box.send_keys(query)
    search_button.click()

    found = {}

    i = 0
    while True:
        username = ut.find_element_id(driver, 'teacher' + str(i) + '-username', msg)
        first_name = ut.find_element_id(driver, 'teacher' + str(i) + '-first_name', msg)
        last_name = ut.find_element_id(driver, 'teacher' + str(i) + '-last_name', msg)
        if username is None or first_name is None or last_name is None:
            break
        username = username.text.strip()
        first_name = first_name.text.strip()
        last_name = last_name.text.strip()
        found[username] = (first_name, last_name)
        i += 1

    for user in correct_list:
        if user.username not in found:
            return failed('13', msg)
        if found[user.username][0] != user.first_name:
            return failed('13', msg)
        if found[user.username][1] != user.last_name:
            return failed('13', msg)

    for user in wrong_list:
        if user.username in found:
            return failed('13', msg)

    return passed('13')


def test_14(ip, group_id, driver):
    msg = ''
    user = User([False])
    event = Event(user)
    if not ut.connect(ip, driver, msg):
        return failed('14', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('14', msg)
    # home_url = driver.current_url
    # home_source = driver.page_source
    if not user.signup(driver, msg, send_type=True):
        return failed('14', msg)
    if not event.create(driver, msg):
        return failed('14', msg)
    # if driver.current_url != home_url or driver.page_source != home_source:
    #     return failed('14', 'redirect to home after creation failed')
    ut.login_to_django_admin(group_id=group_id, driver=driver, ip=ip, msg=msg)
    if not ut.check_event_in_django_admin(ip, event, driver, msg):
        return failed('14', msg)
    #
    # TODO check errors

    return passed('14')


def test_23(ip, group_id, driver):
    msg = ''
    options = [True, False]
    for i in range(2):
        user = User(options)
        options.remove(user.is_student)
        if not ut.connect(ip, driver, msg):
            return failed('23', msg)
        if not ut.check_navbar(False, driver, msg):
            return failed('23', msg)
        home_url = driver.current_url
        home_source = driver.page_source
        if not user.signup(driver, msg, send_type=True):
            return failed('23', msg)
        if driver.current_url != home_url or driver.page_source != home_source:
            return failed('23', 'redirect to home after signup failed')
        if not user.login(driver, msg):
            return failed('23', msg)
        if not user.go_to_profile(driver, msg):
            return failed('23', msg)
        if user.is_student:
            if 'دانشجو' not in driver.page_source:
                return failed('23', msg)
        else:
            if 'استاد' not in driver.page_source:
                return failed('23', msg)
        if not user.logout(driver, msg):
            return failed('23', msg)

    return passed('23')


def test_24(ip, group_id, driver):
    msg = ''
    if not ut.connect(ip, driver, msg):
        return failed('24', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('24', msg)

    query = ut.random_string(random.randint(3, 7))
    # print(query)

    correct_list, wrong_list = prepare_search(driver, query, '24', msg)

    driver.get(ip + '/search_teachers_api/?query=' + query)

    res = json.loads(ut.find_css_selector_element(driver, 'pre', msg).text.strip())
    found = {}

    driver.get(ip)
    user = User()
    if not user.signup(driver, msg, send_type=True):
        return failed('24', msg)
    if not user.login(driver, msg):
        return failed('24', msg)

    for teacher in res:
        driver.get(ip + teacher['profile_url'])
        id_first_name = ut.find_element_id(driver, 'text_firstname', msg)
        id_last_name = ut.find_element_id(driver, 'text_lastname', msg)
        id_user_name = ut.find_element_id(driver, 'text_username', msg)
        if id_first_name is None or id_last_name is None or id_user_name is None:
            return failed('24', msg)
        if id_first_name.text.strip() != teacher['first_name']:
            return failed('24', msg)
        if id_last_name.text.strip() != teacher['last_name']:
            return failed('24', msg)
        found[id_user_name.text.strip()] = (teacher['first_name'], teacher['last_name'])

    for user in correct_list:
        if user.username not in found:
            return failed('24', msg)
        if found[user.username][0] != user.first_name:
            return failed('24', msg)
        if found[user.username][1] != user.last_name:
            return failed('24', msg)

    for user in wrong_list:
        if user.username in found:
            return failed('24', msg)

    return passed('24')


def test_25(ip, group_id, driver):
    msg = ''
    if not ut.connect(ip, driver, msg):
        return failed('25', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('25', msg)

    user = User([False])
    if not user.signup(driver, msg, send_type=True):
        return failed('25', msg)
    if not user.login(driver, msg):
        return failed('25', msg)
    search_box = ut.find_css_selector_element(driver, 'input#search_profiles', msg)
    search_button = ut.find_css_selector_element(driver, 'button#search_profiles', msg)
    if search_box is None or search_button is None:
        return failed('25', msg)
    search_box.send_keys(user.username)
    search_button.click()
    username_link = None
    for a in driver.find_elements_by_xpath("//a"):
        if a.text == user.username:
            username_link = a
            break
    if username_link is None:
        return failed('25', msg)
    username_link.click()
    source = driver.page_source
    if user.first_name not in source or user.last_name not in source or user.username not in source:
        return failed('25', "incorrect or wrong user profile information")
    return passed('25')
