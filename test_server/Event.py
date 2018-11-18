import utils as ut
import random
import time


class Event:
    def __init__(self, user):
        self.user = user
        self.date = time.strftime('%Y-%m-%d', ut.random_date_time())
        btime = ut.random_date_time()
        self.begin_time = time.strftime('%H:%M:%S', btime)
        self.end_time = time.strftime('%H:%M:%S', ut.random_time_gt(btime))
        self.capacity = random.randint(1, 5)

    def create(self, driver, msg):
        self.user.logout(driver, msg)
        if not self.user.login(driver, msg):
            return False
        create_link = ut.find_element_id(driver, "navbar_new_free_time", msg)
        if create_link is None:
            return False
        create_link.click()
        id_date = ut.find_element_id(driver, "id_start_0", msg)
        id_begin_time = ut.find_element_id(driver, "id_start_1", msg)
        id_end_time = ut.find_element_id(driver, "id_end", msg)
        id_capacity = ut.find_element_id(driver, "id_student_capacity", msg)
        if id_begin_time is None or id_capacity is None or id_date is None or id_end_time is None:
            return False
        id_end_time.send_keys(self.end_time)
        id_date.send_keys(self.date)
        id_begin_time.send_keys(self.begin_time)
        id_capacity.send_keys(self.capacity)

        id_submit = ut.find_element_id(driver, "form_submit", msg)
        if id_submit is None:
            return False
        id_submit.click()
        return True


