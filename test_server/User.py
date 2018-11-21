import utils as ut
import random


class User:
    def __init__(self, valid_is_students=[True]):
        self.first_name = ut.random_string(10)
        self.last_name = ut.random_string(10)
        self.username = ut.random_string(10)
        self.email = ut.random_email()
        self.password = ut.random_string(10)
        self.is_student = random.choice(valid_is_students)

    def signup(self, driver, msg, send_mismatched_password=False, send_type=True):
        ut.find_element_id(driver, "id_navbar_signup", msg).click()
        id_first_name = ut.find_element_id(driver, "id_first_name", msg)
        id_last_name = ut.find_element_id(driver, "id_last_name", msg)
        id_username = ut.find_element_id(driver, "id_username", msg)
        id_email = ut.find_element_id(driver, "id_email", msg)
        id_password1 = ut.find_element_id(driver, "id_password1", msg)
        id_password2 = ut.find_element_id(driver, "id_password2", msg)
        id_type_student = ut.find_element_id(driver, "id_type_0", msg)
        id_type_teacher = ut.find_element_id(driver, "id_type_1", msg)
        if id_first_name is None or id_last_name is None or id_username is None \
                or id_email is None or id_password1 is None or id_password2 is None:
            msg.append("cant signup")
            return False
        id_first_name.send_keys(self.first_name)
        id_last_name.send_keys(self.last_name)
        id_username.send_keys(self.username)
        id_email.send_keys(self.email)
        id_password1.send_keys(self.password)
        if send_mismatched_password:
            id_password2.send_keys(self.password + ut.random_string(10))
        else:
            id_password2.send_keys(self.password)
        if send_type:
            if id_type_teacher is None or id_type_student is None:
                msg.append("user type not found")
                return False
            if self.is_student:
                id_type_student.click()
            else:
                id_type_teacher.click()
        signup_submit = ut.find_element_id(driver, "id_submit", msg)
        if signup_submit is None:
            return False
        signup_submit.click()
        return True

    def login(self, driver, msg):
        navbar_login = ut.find_element_id(driver, "id_navbar_login", msg)
        if navbar_login is None:
            return False
        navbar_login.click()
        id_username = ut.find_element_id(driver, "id_username", msg)
        id_password = ut.find_element_id(driver, "id_password", msg)
        if id_username is None or id_password is None:
            return False
        id_username.send_keys(self.username)
        id_password.send_keys(self.password)
        login_submit = ut.find_element_id(driver, "id_submit", msg)
        if login_submit is None:
            return False
        login_submit.click()
        return True

    def logout(self, driver, msg):
        navbar_logout = ut.find_element_id(driver, "id_navbar_logout", msg)
        if navbar_logout is None:
            return False
        navbar_logout.click()
        return True

    def go_to_profile(self, driver, msg):
        navbar_profile = ut.find_element_id(driver, "id_navbar_profile", msg)
        if navbar_profile is None:
            return False
        navbar_profile.click()
        return True

    def reserve(self, event, driver, msg):
        if not ut.search(event.user.username, driver, msg):
            return False

        id_profile = ut.find_element_id(driver, 'teacher0-username', msg)
        if id_profile is None:
            return False
        id_profile.click()

        i = 0
        id_reserve = None
        while True:
            id_event = ut.find_element_id(driver, 'free-time-' + str(i), msg)
            if id_event is None:
                break
            source = id_event.text
            if event.date in source and event.begin_time in source and event.end_time in source and str(event.capacity) in source:
                id_reserve = ut.find_element_id(id_event, 'reserve-free-time', msg)
                if id_reserve is None:
                    return False
                break
            i += 1
        if id_reserve is None:
            return False
        id_reserve.click()
        return True

    def anti_reserve(self, event, driver, msg):
        if not self.go_to_profile(driver, msg):
            return False
        i = 0
        while True:
            id_res = ut.find_element_id(driver, 'reserved-free-time-' + str(i), msg)
            if id_res is None:
                break
            source = id_res.text
            if event.user.first_name in source and event.user.last_name in source and event.date in source and event.begin_time in source and event.end_time in source:
                id_res = ut.find_element_id(driver, "cancel_meeting", msg)
                if id_res is None:
                    return False
                id_res.click()
                return True
            i += 1
        return False

