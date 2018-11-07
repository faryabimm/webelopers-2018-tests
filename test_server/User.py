import utils as ut


class User:
    def __init__(self):
        self.first_name = ut.random_string(10)
        self.last_name = ut.random_string(10)
        self.username = ut.random_string(10)
        self.email = ut.random_email()
        self.password = ut.random_string(10)

    def signup(self, driver, msg, send_mismatched_password=False):
        ut.find_element_id(driver, "navbar_signup", msg).click()
        id_first_name = ut.find_element_id(driver, "id_first_name", msg)
        id_last_name = ut.find_element_id(driver, "id_last_name", msg)
        id_username = ut.find_element_id(driver, "id_username", msg)
        id_email = ut.find_element_id(driver, "id_email", msg)
        id_password1 = ut.find_element_id(driver, "id_password1", msg)
        id_password2 = ut.find_element_id(driver, "id_password2", msg)
        if id_first_name is None or id_last_name is None or id_username is None \
                or id_email is None or id_password1 is None or id_password2 is None:
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
        signup_submit = ut.find_element_id(driver, "signup_submit", msg)
        if signup_submit is None:
            return False
        signup_submit.click()
        return True

    def login(self, driver, msg):
        navbar_login = ut.find_element_id(driver, "navbar_login", msg)
        if navbar_login is None:
            return False
        navbar_login.click()
        id_username = ut.find_element_id(driver, "id_username", msg)
        id_password = ut.find_element_id(driver, "id_password", msg)
        if id_username is None or id_password is None:
            return False
        id_username.send_keys(self.username)
        id_password.send_keys(self.password)
        login_submit = ut.find_element_id(driver, "login_submit", msg)
        if login_submit is None:
            return False
        login_submit.click()
        return True

    def logout(self, driver, msg):
        navbar_logout = ut.find_element_id(driver, "navbar_logout", msg)
        if navbar_logout is None:
            return False
        navbar_logout.click()
        return True