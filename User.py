import utils as ut


class User:
    def __init__(self):
        self.first_name = ut.random_string(10)
        self.last_name = ut.random_string(10)
        self.username = ut.random_string(10)
        self.email = ut.random_email()
        self.password = ut.random_string(10)

    def signup(self, driver):
        ut.find_element_id(driver, "navbar_signup", driver).click()
        id_first_name = ut.find_element_id(driver, "id_first_name", driver)
        id_last_name = ut.find_element_id(driver, "id_last_name", driver)
        id_username = ut.find_element_id(driver, "id_username", driver)
        id_email = ut.find_element_id(driver, "id_email", driver)
        id_password1 = ut.find_element_id(driver, "id_password1", driver)
        id_password2 = ut.find_element_id(driver, "id_password2", driver)
        if id_first_name is None or id_last_name is None or id_username is None \
                or id_email is None or id_password1 is None or id_password2 is None:
            return False
        id_first_name.send_keys(self.first_name)
        id_last_name.send_keys(self.last_name)
        id_username.send_keys(self.username)
        id_email.send_keys(self.email)
        id_password1.send_keys(self.password)
        id_password2.send_keys(self.password)
        signup_submit = ut.find_element_id(driver, "signup_submit", driver)
        if signup_submit is None:
            return False
        signup_submit.click()
        return True

    def login(self, driver):
        pass
