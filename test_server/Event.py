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
        self.old = None

    def new(self):
        self.old = Event(self.user)
        self.old.date = self.date
        self.old.begin_time = self.begin_time
        self.old.end_time = self.end_time
        self.old.capacity = self.capacity

        self.date = time.strftime('%Y-%m-%d', ut.random_date_time())
        btime = ut.random_date_time()
        self.begin_time = time.strftime('%H:%M:%S', btime)
        self.end_time = time.strftime('%H:%M:%S', ut.random_time_gt(btime))
        # self.capacity = random.randint(1, 5)

    def create(self, driver, msg, logout_login=True):
        if logout_login:
            if not self.user.logout(driver, msg):
                msg.pop()
            if not self.user.login(driver, msg):
                return False
        create_link = ut.find_element_id(driver, "id_navbar_meeting", msg)
        if create_link is None:
            return False
        create_link.click()
        id_date = ut.find_element_id(driver, "id_date", msg)
        id_begin_time = ut.find_element_id(driver, "id_start", msg)
        id_end_time = ut.find_element_id(driver, "id_end", msg)
        id_capacity = ut.find_element_id(driver, "id_student_capacity", msg)
        if id_begin_time is None or id_capacity is None or id_date is None or id_end_time is None:
            return False
        id_end_time.send_keys(self.end_time)
        id_date.send_keys(self.date)
        id_begin_time.send_keys(self.begin_time)
        id_capacity.send_keys(self.capacity)

        id_submit = ut.find_element_id(driver, "id_submit", msg)
        if id_submit is None:
            return False
        id_submit.click()
        return True

    def save(self, driver, msg, logout_login=True):
        if logout_login:
            self.user.logout(driver, msg)
            if not self.user.login(driver, msg):
                return False
        id_profile = ut.find_element_id(driver, 'id_navbar_profile', msg)
        if id_profile is None:
            return False
        id_profile.click()

        i = 0
        id_change = None
        while True:
            id_event = ut.find_element_id(driver, 'id_meeting_' + str(i), msg)
            if id_event is None:
                msg.pop()
                break
            source = id_event.text
            # print(source)
            # print(self.old.date)
            # print(self.old.begin_time)
            # print(self.old.end_time)
            # print(self.old.capacity)
            if self.old.date in source and self.old.begin_time in source and self.old.end_time in source and str(self.old.capacity) in source:
                id_change = ut.find_element_id(id_event, 'id_edit_meeting', msg)
                if id_change is None:
                    return False
                break
            i += 1
        if id_change is None:
            return False
        id_change.click()
        id_date = ut.find_element_id(driver, "id_date", msg)
        id_begin_time = ut.find_element_id(driver, "id_start", msg)
        id_end_time = ut.find_element_id(driver, "id_end", msg)
        id_capacity = ut.find_element_id(driver, "id_student_capacity", msg)
        if id_begin_time is None or id_capacity is None or id_date is None or id_end_time is None:
            return False
        id_end_time.clear()
        id_end_time.send_keys(self.end_time)
        id_date.clear()
        id_date.send_keys(self.date)
        id_begin_time.clear()
        id_begin_time.send_keys(self.begin_time)
        id_capacity.clear()
        id_capacity.send_keys(self.capacity)

        id_submit = ut.find_element_id(driver, "id_submit", msg)
        if id_submit is None:
            return False
        id_submit.click()
        return True

    def delete(self, driver, msg, logout_login=True):
        if logout_login:
            self.user.logout(driver, msg)
            if not self.user.login(driver, msg):
                return False
        id_profile = ut.find_element_id(driver, 'id_navbar_profile', msg)
        if id_profile is None:
            return False
        id_profile.click()

        i = 0
        id_change = None
        while True:
            id_event = ut.find_element_id(driver, 'id_meeting_' + str(i), msg)
            if id_event is None:
                break
            source = id_event.text
            if self.date in source and self.begin_time in source and self.end_time in source and str(self.capacity) in source:
                id_change = ut.find_element_id(id_event, 'id_edit_meeting', msg)
                if id_change is None:
                    return False
                break
            i += 1
        if id_change is None:
            return False
        id_change.click()
        id_remove = ut.find_element_id(driver, 'id_remove_meeting', msg)
        if id_remove is None:
            return False
        id_remove.click()
        return True


