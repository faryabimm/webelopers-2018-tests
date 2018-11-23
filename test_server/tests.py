import json
import os
import random
import time
import urllib.request

import numpy
import utils as ut
from ContactMessage import ContactMessage
from Event import Event
from PIL import Image
from User import User
from markdown import markdown
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def failed(test, message):
    return False, 'TEST {}: {}'.format(test, message)


def passed(test):
    return True, 'TEST {}: passed!'.format(test)


def test_1(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('1', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('1', msg)

    if "به سامانه استادجو خوش" not in driver.page_source:
        return failed('1', 'incorrect or not found welcome message')

    home_url = driver.current_url
    home_source = driver.page_source
    ut.find_element_id(driver, "id_navbar_home", msg).click()
    if "به سامانه استادجو خوش" not in driver.page_source:
        return failed('1', "incorrect or not found welcome message")

    return passed('1')


def test_2(ip, group_id, driver):
    msg = []
    user = User()
    if not ut.connect(ip, driver, msg):
        return failed('2', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('2', msg)
    home_url = driver.current_url
    home_source = driver.page_source
    if not user.signup(driver, msg, send_type=False):
        return failed('2', msg)
    ut.login_to_django_admin(group_id=group_id, driver=driver, ip=ip, msg=msg)
    if not ut.check_user_in_django_admin(ip, user, driver, msg):
        msg.append("line 59 call a staff, maybe superuser with admin and password=passomass not set or not using django\'s defualt User model or you are EZed")
        return failed('2', msg)

    return passed('2')


# user assumed to be signed up to the site
# this test is dependent to test 2 for user signup
def test_3(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('3', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('3', msg)
    user_1 = User()
    if not user_1.signup(driver, msg, send_type=False):
        return failed('3', msg)
    driver.delete_all_cookies()
    if not ut.connect(ip, driver, msg):
        return failed('3', msg)
    if not user_1.login(driver, msg):
        return failed('3', msg)
    # checking right user
    if not ut.check_navbar(True, driver, msg):
        return failed('3', msg)
    login_error_message = "نام کاربری یا گذرواژه"
    if login_error_message in driver.page_source:
        return failed('3', 'no login message error shown')
    if not ut.connect(ip, driver, msg):
        return failed('3', msg)
    driver.delete_all_cookies()
    # checking wrong user
    if not ut.connect(ip, driver, msg):
        return failed('3', msg)
    # print(driver.page_source)
    driver.delete_all_cookies()
    wrong_user = User()
    if not wrong_user.login(driver, msg):
        return failed('3', msg)
    if login_error_message not in driver.page_source:
        return failed('3', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('3', msg)

    return passed('3')


def test_4(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('4', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('4', msg)
    user_exists = "کاربری با نام کاربری وارد شده وجود دارد"
    email_exists = "کاربری با ایمیل وارد شده وجود دارد"
    password_mismatch = "گذرواژه و تکرار گذرواژه یکسان نیستند"
    # all correct
    user_1 = User()
    if not user_1.signup(driver, msg, send_type=False):
        return failed('4', msg)
    if not ut.connect(ip, driver, msg):
        return failed('4', msg)
    source_1 = driver.page_source
    if user_exists in source_1:
        return failed('4', error_msg)
    driver.delete_all_cookies()

    # username error
    user_2 = User()
    user_2.username = user_1.username
    user_2.signup(driver, msg, send_type=False)
    source_2 = driver.page_source
    if user_exists not in source_2 or email_exists in source_2 or password_mismatch in source_2:
        msg.append("wrong error messages shown in signup errors")
        return failed('4', msg)
    driver.delete_all_cookies()

    # email error
    user_3 = User()
    user_3.email = user_1.email
    user_3.signup(driver, msg, send_type=False)
    source_3 = driver.page_source
    if email_exists not in source_3 or user_exists in source_3 or password_mismatch in source_3:
        msg.append("wrong error messages shown in signup errors")
        return failed('4', msg)
    driver.delete_all_cookies()

    # password mismatch error
    user_4 = User()
    user_4.signup(driver, msg, send_mismatched_password=True, send_type=False)
    
    source_4 = driver.page_source
    if password_mismatch not in source_4 or user_exists in source_4 or email_exists in source_4:
        msg.append("password mismatch")
        return failed('4', msg)
    ut.login_to_django_admin(group_id=group_id, driver=driver, ip=ip, msg=msg)
    if not ut.check_user_in_django_admin(ip, user_1, driver, msg):
        msg.append("ADD THAT FUCKING ADMIN, PASSOMASS TO YOUR DJANGO ADMINS AND PLEASE SET THE LANG TO en-US")
        return failed('4', msg)
    if ut.check_user_in_django_admin(ip, user_2, driver, msg):
        return failed('4', msg)
    if ut.check_user_in_django_admin(ip, user_3, driver, msg):
        return failed('4', msg)
    if ut.check_user_in_django_admin(ip, user_4, driver, msg):
        return failed('4', msg)
    return passed('4')


def submit_contact_us(ip, group_id, driver, msg):
    if not ut.connect(ip, driver, msg):
        return None
    if not ut.check_navbar(False, driver, msg):
        return None
    navbar = ut.find_element_id(driver, "id_navbar", msg)
    if navbar is None:
        return None
    contact_us = ut.find_element_id(navbar, "id_navbar_contact_us", msg)
    if contact_us is None:
        return None
    contact_us.click()
    title_field = ut.find_element_id(driver, "id_title", msg)
    email_field = ut.find_element_id(driver, "id_email", msg)
    text_field = ut.find_element_id(driver, "id_text", msg)
    submit_button = ut.find_element_id(driver, "id_submit", msg)
    if title_field is None or email_field is None or text_field is None or submit_button is None:
        return None
    if email_field.get_attribute("type") != "email":
        msg.append("email field type is not email")
        return None
    message = ContactMessage()
    title_field.send_keys(message.title)
    email_field.send_keys(message.email)
    text_field.send_keys(message.text)
    submit_button.click()
    return message


def test_5(ip, group_id, driver):
    msg = []
    # TODO: TOO SLOW AND BLOCKING
    message = submit_contact_us(ip, group_id, driver, msg)
    if message is None:
        return failed('5', msg)
    submitted = WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.XPATH, "//*"), "درخواست شما ثبت شد"))
    if submitted is None:
        return failed('5', "sending email took too long time or failed somehow")

    return passed('5')


def test_6(ip, group_id, driver):
    msg = []
    message = submit_contact_us(ip, group_id, driver, msg)
    if message is None:
        return failed('6', msg)
    for i in range(10):
        if not ut.connect("https://www.fastmail.com/login/", driver, msg):
            return failed('6', msg)
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element((By.XPATH, "//*"), "Log In"))
        username_field = ut.find_element_name(driver, "username", msg)
        password_field = ut.find_element_name(driver, "password", msg)
        login_button = ut.find_css_selector_element(driver, "button", msg)
        if username_field is None or password_field is None or login_button is None:
            return failed('6', msg)
        username_field.send_keys("ostadju@fastmail.com")
        password_field.send_keys("thegreatramz")
        login_button.click()
        if not ut.connect("https://www.fastmail.com/mail/Inbox", driver, msg):
            msg.append("connection to fastmail failed call a staff NOW")
            return failed('6', msg)
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//*"), "No Conversation Selected"))
        title_link = ut.find_css_selector_element(driver, "div[title={}]".format(message.title), msg)
        if title_link is None:
            return failed('6', msg)
        title_link.click()
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.XPATH, "//*"), "Reply"))
        source = driver.page_source
        if message.text not in source or message.email not in source:
            # print(source)
            # print(message.text)
            # print(message.email)
            return failed('6', "contact us message hasn't sent correctly")
        return passed('6')


def test_7(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('7', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('7', msg)
    if ut.find_element_id(driver, "id_navbar", msg) is None:
        return failed('7', msg)
    user_1 = User()
    if not user_1.signup(driver, msg, send_type=False):
        return failed('7', msg)
    if not user_1.login(driver, msg):
        return failed('7', msg)
    if not ut.check_navbar(True, driver, msg):
        return failed('7', msg)
    user_1.logout(driver, msg)
    if "به سامانه استادجو خوش آمدید" not in driver.page_source:
        return failed('7', 'incorrect or not found welcome message')
    if not ut.check_navbar(False, driver, msg):
        return failed('7', msg)
    return passed('7')


def create_user_goto_profile(ip, group_id, driver, msg):
    if not ut.connect(ip, driver, msg):
        return None
    if not ut.check_navbar(False, driver, msg):
        return None
    navbar = ut.find_element_id(driver, "id_navbar", msg)
    if navbar is None:
        return None
    user_1 = User()
    if not user_1.signup(driver, msg, send_type=False):
        return None
    if not user_1.login(driver, msg):
        return None
    profile = ut.find_element_id(driver, "id_navbar_profile", msg)
    if profile is None:
        msg.append("profile link not found on navbar after login")
        return None
    profile = ut.find_element_id(driver, "id_navbar_profile", msg)
    if profile is None:
        return None
    profile.click()
    return user_1


def test_8(ip, group_id, driver):
    msg = []
    user_1 = create_user_goto_profile(ip, group_id, driver, msg)
    if user_1 is None:
        return failed('8', msg)
    source = driver.page_source
    if user_1.first_name not in source or user_1.last_name not in source or user_1.username not in source:
        msg.append("incorrect user profile information")
        return failed('8', msg)
    return passed('8')


def test_9(ip, group_id, driver):
    msg = []
    user_1 = create_user_goto_profile(ip, group_id, driver, msg)
    if user_1 is None:
        return failed('9', msg)
    edit_profile = ut.find_element_id(driver, "id_edit_profile", msg)
    if edit_profile is None:
        return failed('9', msg)
    edit_profile.click()
    field_first_name = ut.find_element_id(driver, "id_first_name", msg)
    field_last_name = ut.find_element_id(driver, "id_last_name", msg)
    submit_button = ut.find_element_id(driver, "id_submit", msg)
    if field_first_name is None or field_last_name is None or submit_button is None:
        return failed('9', msg)
    first_name = ut.random_string(15)
    last_name = ut.random_string(15)
    field_first_name.clear()
    field_last_name.clear()
    field_first_name.send_keys(first_name)
    field_last_name.send_keys(last_name)
    submit_button.click()
    field_first_name = ut.find_element_id(driver, "id_first_name", msg)
    field_last_name = ut.find_element_id(driver, "id_last_name", msg)
    if field_first_name is None or field_last_name is None:
        return failed('9', msg)
    if first_name not in field_first_name.text or last_name not in field_last_name.text:
        msg.append("profile edit hasn't completed correctly")
        return failed('9', msg)
    return passed('9')


def test_10(ip, group_id, driver):
    msg = []
    user_1 = create_user_goto_profile(ip, group_id, driver, msg)
    if user_1 is None:
        return failed('10', msg)
    edit_profile = ut.find_element_id(driver, "id_edit_profile", msg)
    if edit_profile is None:
        return failed('9', msg)
    edit_profile.click()
    bio_field = ut.find_element_id(driver, "id_bio", msg)
    # FIXME this gender_select heavily depends on site's model and may fail
    gender_select = ut.find_element_id(driver, "id_gender", msg)
    gender_option = {}
    gender_option['M'] = ut.find_css_selector_element(driver, "option[value=M]", msg)
    gender_option['F'] = ut.find_css_selector_element(driver, "option[value=F]", msg)
    submit = ut.find_element_id(driver, "id_submit", msg)
    if bio_field is None or gender_select is None or submit is None \
            or gender_option['M'] is None or gender_option['F'] is None:
        return failed('10', msg)
    user_1.bio = ut.random_string(200)
    bio_field.send_keys(user_1.bio)
    user_1.gender = random.choice(['M', 'F'])
    gender_option[user_1.gender].click()
    submit.click()
    if user_1.bio not in driver.page_source:
        msg.append("user bio has not been saved in profile")
        return failed('10', msg)
    text_gender = ut.find_element_id(driver, "id_gender", msg)
    if text_gender is None:
        return failed('10', msg)
    gender = {'M': "مرد", 'F': "زن"}
    if gender[user_1.gender] not in text_gender.text:
        msg.append("user gender has not been saved correctly")
        return failed('10', msg)
    return passed('10')


def test_11(ip, group_id, driver):
    msg = []
    user_1 = create_user_goto_profile(ip, group_id, driver, msg)
    if user_1 is None:
        return failed('11', msg)
    edit_profile = ut.find_element_id(driver, "id_edit_profile", msg)
    if edit_profile is None:
        return failed('11', msg)
    edit_profile.click()
    pic_upload = ut.find_element_id(driver, "id_picture", msg)
    submit = ut.find_element_id(driver, "id_submit", msg)
    if pic_upload is None or submit is None:
        return failed('11', msg)
    imarray = numpy.random.rand(100, 100, 3) * 255
    im = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
    im.save('sour.png')
    path = pic_upload.send_keys(os.path.abspath('sour.png'))
    submit.click()
    profile_pic = ut.find_element_id(driver, "id_picture", msg)
    if profile_pic is None:
        return failed('11', msg)
    src = profile_pic.get_attribute('src')
    urllib.request.urlretrieve(src, "temp.png")
    img1 = numpy.asarray(Image.open('sour.png'))
    img2 = numpy.asarray(Image.open('temp.png'))
    if numpy.amax(img1 - img2) != 0 or numpy.amin(img1 - img2) != 0:
        msg.append("it seems the profile image has not been uploaded correctly")
        return failed('11', msg)
    return passed('11')


def test_12(ip, group_id, driver):
    simple = [["{}\n="],
              ["# {}"],
              ["## {}"],
              ["### {}"],
              ["#### {}"],
              ["##### {}"],
              ["###### {}"],
              ["`{}`"],
              ["*_{}__"],
              ["_{}*"]]
    lists = [["* {}"],
             ["1. {}"]]
    sn = numpy.random.permutation(10)
    s, text = [], ""
    for i in range(10):
        s.append(random.choice(simple))
        s[i] = simple[sn[i]]
        s[i].append(ut.random_string(15))
        text += "\n" + s[i][0].format(s[i][1]) + "\n"
    ln = numpy.random.permutation(2)
    for i in range(2):
        t = "\n{}\n\n".format(ut.random_string(20))
        for j in range(5):
            t += lists[ln[i]][0].format(ut.random_string(15)) + "\n"
        text += t
    result = markdown(text)
    msg = []
    user_1 = create_user_goto_profile(ip, group_id, driver, msg)
    if user_1 is None:
        return failed('12', msg)
    edit_profile = ut.find_element_id(driver, "id_edit_profile", msg)
    if edit_profile is None:
        return failed('12', msg)
    edit_profile.click()
    bio = ut.find_element_id(driver, "id_bio", msg)
    if bio is None:
        return failed('12', msg)
    bio.send_keys(text)
    submit = ut.find_element_id(driver, "id_submit", msg)
    if submit is None:
        return failed('12', msg)
    submit.click()
    if result not in driver.page_source:
        msg.append("bio has not been saved correctly")
        return failed('12', msg)
    return passed('12')


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
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('13', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('13', msg)

    query = ut.random_string(random.randint(3, 7))
    # print(query)

    correct_list, wrong_list = prepare_search(driver, query, '13', msg)

    if not ut.search(query, driver, msg):
        return failed('13', msg)

    found = {}

    i = 0
    while True:
        teacher = ut.find_element_id(driver, 'id_teacher_' + str(i), msg)
        if teacher is None:
            msg.pop()
            break
        username = ut.find_element_id(teacher, 'id_username', msg)
        first_name = ut.find_element_id(teacher, 'id_first_name', msg)
        last_name = ut.find_element_id(teacher, 'id_last_name', msg)
        if username is None or first_name is None or last_name is None:
            return failed('13', msg)
        username = username.text.strip()
        first_name = first_name.text.strip()
        last_name = last_name.text.strip()
        found[username] = (first_name, last_name)
        i += 1

    for user in correct_list:
        if user.username not in found:
            msg.append('username not found for one of teachers')
            return failed('13', msg)
        if found[user.username][0] != user.first_name:
            msg.append('first name not found for one of teachers')
            return failed('13', msg)
        if found[user.username][1] != user.last_name:
            msg.append('last name not found for one of teachers')
            return failed('13', msg)

    for user in wrong_list:
        if user.username in found:
            msg.append('wrong teachers found')
            return failed('13', msg)

    return passed('13')


def test_14(ip, group_id, driver):
    msg = []
    user = User([False])
    event = Event(user)
    if not ut.connect(ip, driver, msg):
        return failed('14', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('14', msg)
    if not user.signup(driver, msg, send_type=True):
        return failed('14', msg)
    if not event.create(driver, msg):
        return failed('14', msg)

    driver.get(ip)
    driver.delete_all_cookies()

    # todo
    ##################
    #ut.login_to_django_admin(group_id=group_id, driver=driver, ip=ip, msg=msg)
    #if not ut.check_event_in_django_admin(ip, event, driver, msg):
    #    return failed('14', msg)
    ##################

    driver.get(ip)
    # if not user.logout(driver, msg):
    #     return failed('14', msg)
    #
    # TODO check errors

    error_conflict = 'بازه زمانی انتخاب شده با فرصت های قبلی شما اشتراک دارد'
    error_begin_end = 'زمان شروع باید قبل از زمان پایان فرصت باشد'
    error_invalid_begin = 'زمان شروع وارد شده معتبر نمی‌باشد'
    error_invalid_end = 'زمان پایان وارد شده معتبر نمی‌باشد'
    error_invalid_date = 'تاریخ وارد شده معتبر نمی‌باشد'

    date1 = time.strftime('%Y-%m-%d', ut.random_date_time())
    date2 = time.strftime('%Y-%m-%d', ut.random_date_time())
    time1 = ut.random_date_time()
    time2 = ut.random_time_gt(time1)
    time3 = ut.random_time_gt(time2)
    time4 = ut.random_time_gt(time3)
    time1 = time.strftime('%H:%M:%S', time1)
    time2 = time.strftime('%H:%M:%S', time2)
    time3 = time.strftime('%H:%M:%S', time3)
    time4 = time.strftime('%H:%M:%S', time4)
    invalid_second = random.randint(61, 80)
    invalid_hour = random.randint(24, 30)
    invalid_time1 = time.strftime('%H:%M:', ut.random_date_time()) + str(invalid_second)
    invalid_time2 = time.strftime('%H:', ut.random_date_time()) + str(invalid_second) + time.strftime(':%S',
                                                                                                      ut.random_date_time())
    invalid_time3 = str(invalid_hour) + time.strftime(':%M:%S', ut.random_date_time())
    invalid_time4 = ut.random_string(8)
    invalid_day = random.randint(32, 40)
    invalid_month = random.randint(13, 20)
    invalid_date1 = time.strftime('%Y-%m-', ut.random_date_time()) + str(invalid_day)
    invalid_date2 = time.strftime('%Y-', ut.random_date_time()) + str(invalid_month) + time.strftime('-%d',
                                                                                                     ut.random_date_time())
    invalid_date3 = ut.random_string(10)

    dates = [date1, date2, invalid_date1, invalid_date2, invalid_date3]
    times = [time1, time2, time3, time4, invalid_time1, invalid_time2, invalid_time3, invalid_time4]
    errors = [None, error_conflict, error_begin_end, error_invalid_begin, error_invalid_end, error_invalid_date]

    # print(times)
    # print(dates)
    # print(user.username)

    test_cases = [{'d1': 0, 'd2': 0, 'b1': 0, 'e1': 3, 'b2': 1, 'e2': 2, 'a': 1, 'n': True},
                  {'d1': 0, 'd2': 0, 'b1': 0, 'e1': 2, 'b2': 1, 'e2': 3, 'a': 1, 'n': True},
                  {'d1': 0, 'd2': 0, 'b1': 1, 'e1': 2, 'b2': 0, 'e2': 3, 'a': 1, 'n': True},
                  {'d1': 0, 'd2': 0, 'b1': 1, 'e1': 3, 'b2': 0, 'e2': 2, 'a': 1, 'n': True},
                  {'d1': 0, 'd2': 1, 'b1': 1, 'e1': 3, 'b2': 0, 'e2': 2, 'a': 0, 'n': True},
                  {'d1': 0, 'd2': 1, 'b1': 1, 'e1': 3, 'b2': 2, 'e2': 0, 'a': 2, 'n': True},
                  {'d1': 'x', 'd2': 1, 'b2': 4, 'e2': 0, 'a': 3, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 5, 'e2': 0, 'a': 3, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 6, 'e2': 0, 'a': 3, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 7, 'e2': 0, 'a': 3, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 0, 'e2': 4, 'a': 4, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 0, 'e2': 5, 'a': 4, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 0, 'e2': 6, 'a': 4, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 0, 'e2': 7, 'a': 4, 'n': False},
                  {'d1': 'x', 'd2': 2, 'b2': 0, 'e2': 1, 'a': 5, 'n': False},
                  {'d1': 'x', 'd2': 3, 'b2': 0, 'e2': 1, 'a': 5, 'n': False},
                  {'d1': 'x', 'd2': 4, 'b2': 0, 'e2': 1, 'a': 5, 'n': False}]

    user = None
    for test in test_cases:

        if test['n']:
            user = User([False])
            user.logout(driver, msg)
            if not user.signup(driver, msg, send_type=True):
                return failed('14', msg)

        if test['d1'] != 'x':
            event1 = Event(user)
            event1.date = dates[test['d1']]
            event1.begin_time = times[test['b1']]
            event1.end_time = times[test['e1']]
            if not event1.create(driver, msg, logout_login=test['n']):
                return failed('14', msg)

        event2 = Event(user)
        event2.date = dates[test['d2']]
        event2.begin_time = times[test['b2']]
        event2.end_time = times[test['e2']]
        if not event2.create(driver, msg, logout_login=(test['n'] and test['d1'] == 'x')):
            return failed('14', msg)
        if test['a'] != 0:
            if errors[test['a']] not in driver.page_source:
                msg.append('wrong error msg')
                return failed('14', msg)
        else:
            for i in range(1, len(errors)):
                if errors[i] in driver.page_source:
                    msg.append('wrong error msg')
                    return failed('14', msg)
        # if not user.logout(driver, msg):
        #     return failed('14', msg)

    return passed('14')


def test_22(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('22', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('22', msg)
    login = ut.find_element_id(driver, "id_navbar_login", msg)
    if login is None:
        return failed('22', msg)
    login.click()
    forget = ut.find_element_id(driver, "id_forget_password", msg)
    if forget is None:
        return failed('22', msg)
    forget.click()
    email_field = ut.find_element_id(driver, "id_email", msg)
    if email_field is None:
        return failed('22', msg)
    email_field.send_keys(ut.random_email())
    submit = ut.find_element_id(driver, "id_submit", msg)
    if submit is None:
        return failed('22', msg)
    submit.click()
    if "کاربری با ایمیل داده شده وجود ندار" not in driver.page_source:
        return failed('22', "wrong email entered and there's no error")
    user_1 = User()
    user_1.email = "ostadju@fastmail.com"
    if not user_1.signup(driver, msg):
        return failed('22', msg)
    print(user_1.__dict__)
    login = ut.find_element_id(driver, "id_navbar_login", msg)
    if login is None:
        return failed('22', msg)
    login.click()
    forget = ut.find_element_id(driver, "id_forget_password", msg)
    if forget is None:
        return failed('22', msg)
    forget.click()
    email_field = ut.find_element_id(driver, "id_email", msg)
    if email_field is None:
        return failed('22', msg)
    email_field.send_keys(user_1.email)
    submit = ut.find_element_id(driver, "id_submit", msg)
    if submit is None:
        return failed('22', msg)
    submit.click()
    if "کﺍﺮﺑﺭی ﺏﺍ ﺍیﻡیﻝ ﺩﺍﺪﻫ ﺵﺪﻫ ﻮﺟﻭﺩ ﻥﺩﺍﺭ" in driver.page_source:
        return failed('22', "correct email entered and there's an error message")
    if not ut.connect("https://www.fastmail.com/login/", driver, msg):
        return failed('22', msg)
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.XPATH, "//*"), "Log In"))
    username_field = ut.find_element_name(driver, "username", msg)
    password_field = ut.find_element_name(driver, "password", msg)
    login_button = ut.find_css_selector_element(driver, "button", msg)
    if username_field is None or password_field is None or login_button is None:
        return failed('22', msg)
    username_field.send_keys("ostadju@fastmail.com")
    password_field.send_keys("thegreatramz")
    login_button.click()
    WebDriverWait(driver, 20).until(
        EC.text_to_be_present_in_element((By.XPATH, "//*"), user_1.username))
    title_link = ut.find_css_selector_element(driver, "div[title={}]".format(user_1.username), msg)
    if title_link is None:
        return failed('22', msg)
    title_link.click()
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.XPATH, "//*[contains(@class,'v-ThreadMessage')]"), user_1.username))
    message_body = ut.find_css_selector_element(driver, "div[class=v-Message-body]", msg)
    if message_body is None:
        msg.append("message body is None")
        return failed('22', msg)
    reset = ut.find_css_selector_element(message_body, "a", msg)
    if reset is None:
        msg.append("reset is None")
        return failed('22', msg)
    print(reset.text)
    driver.implicitly_wait(2)
    driver.get(reset.text)

    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation' + 'confirmation popup to appear.')
        alert = driver.switch_to.alert
        alert.accept()
        print("alert accepted")
    except:
        print("no alert")

    pass1 = ut.find_element_id(driver, "id_password1", msg)
    pass2 = ut.find_element_id(driver, "id_password2", msg)
    submit = ut.find_element_id(driver, "id_submit", msg)
    if pass1 is None or pass2 is None or submit is None:
        return failed('22', msg)
    user_1.password = ut.random_string(10)
    pass1.send_keys(user_1.password)
    pass2.send_keys(user_1.password)
    submit.click()
    if not user_1.login(driver, msg):
        return failed('22', "after password change cant login")
    test_26(ip, group_id, driver)
    return passed('22')


def test_15(ip, group_id, driver):
    msg = []
    user1 = User([False])
    event = Event(user1)
    if not ut.connect(ip, driver, msg):
        return failed('15', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('15', msg)
    if not user1.signup(driver, msg, send_type=True):
        return failed('15', msg)
    if not event.create(driver, msg):
        return failed('15', msg)
    if not user1.go_to_profile(driver, msg):
        return failed('15', msg)
    source = driver.page_source
    if event.date not in source or event.begin_time not in source or event.end_time not in source:
        msg.append('some meeting information not found')
        return failed('15', msg)
    return passed('15')


def test_16(ip, group_id, driver):
    msg = []
    user = User([False])
    event = Event(user)
    if not ut.connect(ip, driver, msg):
        return failed('16', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('16', msg)
    if not user.signup(driver, msg, send_type=True):
        return failed('16', msg)
    if not event.create(driver, msg):
        return failed('16', msg)
    event.new()
    if not event.save(driver, msg, logout_login=False):
        return failed('16', msg)
 
    # todo maybe removed
    ####################
    #ut.login_to_django_admin(group_id=group_id, driver=driver, ip=ip, msg=msg)
    #if not ut.check_event_in_django_admin(ip, event, driver, msg):
    #    return failed('16', msg)
    ####################

    driver.get(ip)
    # if not user.logout(driver, msg):
    #     return failed('14', msg)
    #
    # TODO check errors

    error_conflict = 'بازه زمانی انتخاب شده با فرصت های قبلی شما اشتراک دارد'
    error_begin_end = 'زمان شروع باید قبل از زمان پایان فرصت باشد'
    error_invalid_begin = 'زمان شروع وارد شده معتبر نمی‌باشد'
    error_invalid_end = 'زمان پایان وارد شده معتبر نمی‌باشد'
    error_invalid_date = 'تاریخ وارد شده معتبر نمی‌باشد'
    error_capacity = 'ظرفیت جدید کمتر از تعداد رزروها است'

    date1 = time.strftime('%Y-%m-%d', ut.random_date_time())
    date2 = time.strftime('%Y-%m-%d', ut.random_date_time())
    time1 = ut.random_date_time()
    time2 = ut.random_time_gt(time1)
    time3 = ut.random_time_gt(time2)
    time4 = ut.random_time_gt(time3)
    time5 = ut.random_time_gt(time4)
    time6 = ut.random_time_gt(time5)
    time1 = time.strftime('%H:%M:%S', time1)
    time2 = time.strftime('%H:%M:%S', time2)
    time3 = time.strftime('%H:%M:%S', time3)
    time4 = time.strftime('%H:%M:%S', time4)
    time5 = time.strftime('%H:%M:%S', time5)
    time6 = time.strftime('%H:%M:%S', time6)
    invalid_second = random.randint(61, 80)
    invalid_hour = random.randint(24, 30)
    invalid_time1 = time.strftime('%H:%M:', ut.random_date_time()) + str(invalid_second)
    invalid_time2 = time.strftime('%H:', ut.random_date_time()) + str(invalid_second) + time.strftime(':%S',
                                                                                                      ut.random_date_time())
    invalid_time3 = str(invalid_hour) + time.strftime(':%M:%S', ut.random_date_time())
    invalid_time4 = ut.random_string(8)
    invalid_day = random.randint(32, 40)
    invalid_month = random.randint(13, 20)
    invalid_date1 = time.strftime('%Y-%m-', ut.random_date_time()) + str(invalid_day)
    invalid_date2 = time.strftime('%Y-', ut.random_date_time()) + str(invalid_month) + time.strftime('-%d',
                                                                                                     ut.random_date_time())
    invalid_date3 = ut.random_string(10)

    dates = [date1, date2, invalid_date1, invalid_date2, invalid_date3]
    times = [time1, time2, time3, time4, invalid_time1, invalid_time2, invalid_time3, invalid_time4, time5, time6]
    errors = [None, error_conflict, error_begin_end, error_invalid_begin, error_invalid_end, error_invalid_date,
              error_capacity]

    print(dates)
    print(times)
    print(errors)

    test_cases = [{'d1': 0, 'd2': 0, 'b1': 0, 'e1': 3, 'b2': 1, 'e2': 2, 'd3': 0, 'b3': 8, 'e3': 9, 'a': 1, 'n': True},
                  {'d1': 0, 'd2': 0, 'b1': 0, 'e1': 2, 'b2': 1, 'e2': 3, 'd3': 0, 'b3': 8, 'e3': 9, 'a': 1, 'n': True},
                  {'d1': 0, 'd2': 0, 'b1': 1, 'e1': 2, 'b2': 0, 'e2': 3, 'd3': 0, 'b3': 8, 'e3': 9, 'a': 1, 'n': True},
                  {'d1': 0, 'd2': 0, 'b1': 1, 'e1': 3, 'b2': 0, 'e2': 2, 'd3': 0, 'b3': 8, 'e3': 9, 'a': 1, 'n': True},
                  {'d1': 0, 'd2': 1, 'b1': 1, 'e1': 3, 'b2': 0, 'e2': 2, 'd3': 0, 'b3': 8, 'e3': 9, 'a': 0, 'n': True},
                  {'d1': 0, 'd2': 1, 'b1': 1, 'e1': 3, 'b2': 2, 'e2': 0, 'd3': 0, 'b3': 8, 'e3': 9, 'a': 2, 'n': True},
                  {'d1': 'x', 'd2': 1, 'b2': 4, 'e2': 0, 'd3': 'x', 'a': 3, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 5, 'e2': 0, 'd3': 'x', 'a': 3, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 6, 'e2': 0, 'd3': 'x', 'a': 3, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 7, 'e2': 0, 'd3': 'x', 'a': 3, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 0, 'e2': 4, 'd3': 'x', 'a': 4, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 0, 'e2': 5, 'd3': 'x', 'a': 4, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 0, 'e2': 6, 'd3': 'x', 'a': 4, 'n': False},
                  {'d1': 'x', 'd2': 1, 'b2': 0, 'e2': 7, 'd3': 'x', 'a': 4, 'n': False},
                  {'d1': 'x', 'd2': 2, 'b2': 0, 'e2': 1, 'd3': 'x', 'a': 5, 'n': False},
                  {'d1': 'x', 'd2': 3, 'b2': 0, 'e2': 1, 'd3': 'x', 'a': 5, 'n': False},
                  {'d1': 'x', 'd2': 4, 'b2': 0, 'e2': 1, 'd3': 'x', 'a': 5, 'n': False}]

    # ,
    # {'d1': 'x', 'd2': 0, 'b2': 8, 'e2': 9, 'd3': 0, 'b3': 8, 'e3': 9, 'a': 6, 'c3': 5, 'c2': 4, 'n': False}

    user = None
    for test in test_cases:
        # print(test)

        if test['n']:
            user = User([False])
            user.logout(driver, msg)
            if not user.signup(driver, msg, send_type=True):
                return failed('16', msg)

        if test['d1'] != 'x':
            event1 = Event(user)
            event1.date = dates[test['d1']]
            event1.begin_time = times[test['b1']]
            event1.end_time = times[test['e1']]
            if not event1.create(driver, msg, logout_login=test['n']):
                return failed('16', msg)

        if test['d3'] != 'x':
            event2 = Event(user)
            event2.date = dates[test['d3']]
            event2.begin_time = times[test['b3']]
            event2.end_time = times[test['e3']]
            if 'c3' in test:
                event2.capacity = test['c3']
            if not event2.create(driver, msg, logout_login=(test['n'] and test['d1'] == 'x')):
                return failed('16', msg)

        event2.new()
        event2.date = dates[test['d2']]
        event2.begin_time = times[test['b2']]
        event2.end_time = times[test['e2']]
        if 'c2' in test:
            event2.capacity = test['c2']
        if not event2.save(driver, msg, logout_login=(test['n'] and test['d1'] == 'x')):
            return failed('16', msg)

        if test['a'] != 0:
            if errors[test['a']] not in driver.page_source:
                print(test)
                msg.append('wrong error msg')
                return failed('16', msg)
        else:
            for i in range(1, len(errors)):
                if errors[i] in driver.page_source:
                    # print(test)
                    msg.append('wrong error msg')
                    return failed('16', msg)

        if test['a'] != 0:
            event2 = event2.old
        # if not user.logout(driver, msg):
        #     return failed('14', msg)

    return passed('16')


def test_17(ip, group_id, driver):
    msg = []
    user = User([False])
    event = Event(user)
    if not ut.connect(ip, driver, msg):
        return failed('17', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('17', msg)
    if not user.signup(driver, msg, send_type=True):
        return failed('17', msg)
    if not event.create(driver, msg):
        return failed('17', msg)
    if not event.delete(driver, msg, False):
        return failed('17', msg)
    if not user.go_to_profile(driver, msg):
        return failed('17', msg)
    i = 0
    while True:
        id_event = ut.find_element_id(driver, 'id_meeting_' + str(i), msg)
        if id_event is None:
            msg.pop()
            break
        source = id_event.text
        if event.date in source and event.begin_time in source and event.end_time in source and str(
                event.capacity) in source:
            msg.append('not deleted completely')
            return failed('17', msg)
        i += 1

    return passed('17')


def test_18(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('18', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('18', msg)
    user_teacher = User([False])
    event = Event(user_teacher)
    event.capacity = random.randint(2, 4)
    error_full = 'فرصت مورد نظر ظرفیت خالی ندارد'
    if not user_teacher.signup(driver, msg, send_type=True):
        return failed('18', msg)
    if not event.create(driver, msg):
        return failed('18', msg)
    if not user_teacher.logout(driver, msg):
        return failed('18', msg)
    for i in range(event.capacity + 1):
        user_student = User([True])
        if not user_student.signup(driver, msg, send_type=True):
            return failed('18', msg)
        if not user_student.login(driver, msg):
            return failed('18', msg)
        if not user_student.reserve(event, driver, msg):
            return failed('18', msg)
        if i == event.capacity:
            if error_full not in driver.page_source:
                return failed('18', msg)

        # todo maybe replaces with
        ##################
        # else:
        #     ut.login_to_django_admin(group_id=group_id, driver=driver, ip=ip, msg=msg)
        #     if not ut.check_reserve_in_django_admin(ip, event, user_student, driver, msg):
        #         return failed('18', msg)
        ##################
        # else:
        #     if valid not in driver.page_source:
        #         return failed('18', msg)
        ##################

        driver.get(ip)
        if not user_student.logout(driver, msg):
            return failed('18', msg)
    return passed('18')


def test_19(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('19', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('19', msg)
    cnt = random.randint(2, 4)
    events = []
    for i in range(cnt):
        user_teacher = User([False])
        event = Event(user_teacher)
        if not user_teacher.signup(driver, msg, send_type=True):
            return failed('19', msg)
        if not event.create(driver, msg):
            return failed('19', msg)
        if not user_teacher.logout(driver, msg):
            return failed('19', msg)
        events.append(event)
    user_student = User([True])
    if not user_student.signup(driver, msg, send_type=True):
        return failed('19', msg)
    if not user_student.login(driver, msg):
        return failed('19', msg)
    for i in range(cnt):
        if not user_student.reserve(events[i], driver, msg):
            return failed('19', msg)
    if not user_student.go_to_profile(driver, msg):
        return failed('19', msg)
    found = []
    for i in range(cnt):
        id_res = ut.find_element_id(driver, 'id_reserved_meeting_' + str(i), msg)
        if id_res is None:
            return failed('19', msg)
        source = id_res.text
        for event in events:
            if event.user.first_name in source and event.user.last_name in source and event.date in source and event.begin_time in source and event.end_time in source:
                found.append(event)
    if len(found) != len(events):
        return failed('19', msg)
    return passed('19')


def test_20(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('20', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('20', msg)
    user_teacher = User([False])
    event = Event(user_teacher)
    if not user_teacher.signup(driver, msg, send_type=True):
        return failed('20', msg)
    if not event.create(driver, msg):
        return failed('20', msg)
    if not user_teacher.logout(driver, msg):
        return failed('20', msg)
    user_student = User([True])
    if not user_student.signup(driver, msg, send_type=True):
        return failed('20', msg)
    if not user_student.login(driver, msg):
        return failed('20', msg)
    if not user_student.reserve(event, driver, msg):
        return failed('20', msg)
    if not user_student.anti_reserve(event, driver, msg):
        return failed('20', msg)
    if not user_student.go_to_profile(driver, msg):
        return failed('20', msg)
    source = driver.page_source
    if event.user.first_name in source and \
            event.user.last_name in source and \
            event.date in source and event.begin_time in source and event.end_time in source:
        msg.append("student cancled meeting but still visible in his/her profile")
        return failed('20', msg)
    return passed('20')


def find(driver, css_selector, msg):
    element = ut.find_elements_by_id("data")
    if element:
        return element
    else:
        return False


def test_21(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('21', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('21', msg)
    user1 = User([False])
    user2 = User([False])
    if not user1.signup(driver, msg, send_type=True):
        return failed('21', msg)
    if not user1.login(driver, msg):
        return failed('21', msg)
    if not user1.logout(driver, msg):
        return failed('21', msg)
    if not user2.signup(driver, msg, send_type=True):
        return failed('21', msg)
    if not user2.login(driver, msg):
        return failed('21', msg)
    if not user2.logout(driver, msg):
        return failed('21', msg)
    id_search = ut.find_element_id(driver, 'id_search_profiles_input', msg)
    if id_search is None:
        return failed('21', msg)
    id_search.send_keys(user1.username)
    id_res = ut.find_element_id(driver, 'autocomplete_results', msg)
    # print(datetime.datetime.now().time())
    time.sleep(1)
    # submitted = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#autocomplete_results a")))
    # time.sleep(1)
    # EC.number_of_windows_to_be
    submitted = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#autocomplete_results a")))
    if submitted is None:
        return failed('21', msg)
    # print(submitted.text)
    # print(id_res.text)
    # print(help(id_res))
    # print(id_res.get_attribute('innerHTML'))
    # print(id_res.)
    # submitted = WebDriverWait(driver, 10).until(
    #     EC.text_to_be_present_in_element((By.XPATH, "//*"), "درخواست شما ثبت شد"))
    # if submitted is None:
    #     return failed('5', "sending email took too long time")
    # print(id_res.text)
    # print(datetime.datetime.now().time())
    if id_res is None:
        return failed('21', msg)
    if user2.first_name in id_res.text and user2.last_name in id_res.text:
        print(id_res.text)
        msg.append('extra user found')
        return failed('21', msg)
    if user1.first_name not in id_res.text or user1.last_name not in id_res.text:
        # print(1)
        # print(id_res.text)
        # print(user1.first_name)
        # print(user1.last_name)
        msg.append('user not found')
        return failed('21', msg)
    id_link = ut.find_css_selector_element(id_res, 'a', msg)
    if id_link is None:
        return failed('21', msg)
    # print(id_res.text)
    # print(id_link)
    # print(id_res.get_attribute('innerHTML'))
    # print(help(id_link))
    # print(id_link.get_property('href'))
    # submitted.click()
    # source = driver.page_source
    # if user1.first_name not in source or user1.last_name not in source:
    # print(source)
    # return failed('21', msg)
    return passed('21')


def test_23(ip, group_id, driver):
    msg = []
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
        if driver.current_url != home_url:
            msg.append('redirect to home after signup failed')
            return failed('23', msg)

        # todo REMOVE THESE LINES
        #########################
        #########################

    return passed('23')


def test_24(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('24', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('24', msg)

    query = ut.random_string(random.randint(3, 7))
    # print(query)

    correct_list, wrong_list = prepare_search(driver, query, '24', msg)

    driver.get(ip + '/search_teachers_api/?query=' + query)

    # res = json.loads(ut.find_css_selector_element(driver, 'pre', msg).text.strip())
    res = json.loads(driver.page_source.strip())
    found = {}

    driver.get(ip)
    user = User()
    if not user.signup(driver, msg, send_type=True):
        return failed('24', msg)
    if not user.login(driver, msg):
        return failed('24', msg)

    for teacher in res:
        driver.get(ip + teacher['profile_url'])
        id_first_name = ut.find_element_id(driver, 'id_first_name', msg)
        id_last_name = ut.find_element_id(driver, 'id_last_name', msg)
        id_user_name = ut.find_element_id(driver, 'id_username', msg)
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
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('25', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('25', msg)

    user = User([False])
    if not user.signup(driver, msg, send_type=True):
        return failed('25', msg)
    if not user.login(driver, msg):
        return failed('25', msg)
    search_box = ut.find_element_id(driver, 'id_search_profiles_input', msg)
    search_button = ut.find_element_id(driver, 'id_search_profiles_button', msg)
    if search_box is None or search_button is None:
        return failed('25', msg)
    search_box.send_keys(user.username)
    search_button.click()
    username_link = None
    for a in driver.find_elements_by_xpath("//a"):
        if user.username in a.text:
            username_link = a
            break
    if username_link is None:
        return failed('25', msg)
    username_link.click()
    source = driver.page_source
    if user.first_name not in source or user.last_name not in source or user.username not in source:
        return failed('25', "incorrect or wrong user profile information")
    return passed('25')


def test_26(ip, group_id, driver):
    msg = []
    if not ut.connect(ip, driver, msg):
        return failed('26', msg)
    if not ut.check_navbar(False, driver, msg):
        return failed('26', msg)
    user_1 = User()
    if not user_1.signup(driver, msg, send_type=False):
        return failed('26', msg) 
    if not user_1.login(driver, msg):
        return failed('26', msg)
    navbar_profile = ut.find_element_id(driver, "id_navbar_profile", msg)
    if navbar_profile is None:
        return failed('26', msg)
    navbar_profile.click()
    remove_user = ut.find_element_id(driver, "id_remove_user", msg)
    if remove_user is None:
        return failed('26', msg)
    remove_user.click()
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present(), 'Timed out waiting for PA creation ' + 'confirmation popup to appear.')
        alert = driver.switch_to_alert()
        alert.accept()
    except:
        msg.append("test 26 call a staff")
    if not ut.connect(ip, driver, msg):
        return failed('26', msg)
    if not user_1.login(driver, msg):
        return failed('26', msg)
    if "نام کاربری یا گذرواژه" not in driver.page_source:
        msg.append("can login after removing it")
        return failed('26', msg)
    return passed('26')

