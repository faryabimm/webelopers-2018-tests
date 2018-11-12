import utils as ut


class ContactMessage:
    def __init__(self):
        self.title = ut.random_string(10)
        self.email = ut.random_email()
        self.text = ut.random_string(100)
