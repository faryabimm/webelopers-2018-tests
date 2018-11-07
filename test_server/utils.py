import json
import random
import string


def connect(ip, driver, msg):
    try:
        driver.get(ip)
        return True
    except:
        msg += "Connection timed out {}!".format(ip)
        return False


# look_in: found element
# look_for: wanted element id
def find_element_id(look_in, look_for, msg):
    try:
        return look_in.find_element_by_id(look_for)
    except:
        msg += "{} not found".format(look_for)
        return None


def find_element_class(look_in, look_for, msg):
    try:
        return look_in.find_element_by_class_name(look_for)
    except:
        msg += "{} not found".format(look_for)
        return None


def find_element_tag(look_in, look_for, msg):
    try:
        return look_in.find_element_by_tag_name(look_for)
    except:
        msg += "{} not found".format(look_for)
        return None


def find_element_name(look_in, look_for, msg):
    try:
        return look_in.find_element_by_name(look_for)
    except:
        msg += "{} not found".format(look_for)
        return None


def find_css_selector_element(look_in, css_selector, msg):
    try:
        return look_in.find_element_by_css_selector(css_selector)
    except:
        msg += "{} not found".format(css_selector)
        return None


def fill_field(field, text, msg):
    try:
        field.send_keys(text)
        return True
    except:
        msg += "{} not filled".format(field.get_attribute("id"))
        return False


def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def random_email():
    return "{}@{}.{}".format(random_string(random.randint(5, 9)),
                             random_string(random.randint(4, 7)),
                             random_string(random.randint(3, 4)))


def check_navbar(logged_in, driver, msg):
    navbar = find_element_id(driver, "navbar", msg)
    if navbar is None:
        return False
    navbar_home = find_element_id(navbar, "navbar_home", msg)
    if not logged_in:
        navbar_login = find_element_id(navbar, "navbar_login", msg)
        navbar_signup = find_element_id(navbar, "navbar_signup", msg)
        if navbar_login is None or navbar_signup is None or navbar_home is None:
            return False
    else:
        navbar_logout = find_element_id(navbar, "navbar_logout", msg)
        if navbar_home is None or navbar_logout is None:
            return False
    return True


admins = {}


def load_admins(json_file):
    try:
        with open(json_file) as f:
            admins = json.load(f)
            return admins
    except:
        raise Exception("\033[91m FAILED LOADING admins.json \033[0m")


def get_admin(group_id):
    admins = load_admins("admins.json")
    if group_id not in admins.keys():
        raise Exception("\033[91m NO USERNAME AND PASSWORD FOUND FOR GROUP_ID {} \033[0m".format(group_id))
    return admins[group_id]['username'], admins[group_id]['password']


def login_to_django_admin(group_id, driver, ip, msg):
    driver.get(ip + "/admin/auth/user/")
    username, password = get_admin(group_id)
    find_element_name(driver, "username", msg).send_keys(username)
    find_element_name(driver, "password", msg).send_keys(password)
    find_css_selector_element(driver, "form input[type=submit]", msg).click()


def check_user_in_django_admin(ip, user, driver, msg):
    # todo: username password to django admin required
    driver.get(ip + "/admin/auth/user/")
    find_element_id(driver, "searchbar", msg).send_keys(user.username)
    find_css_selector_element(driver, "form input[type=submit]", msg).click()
    field_username = find_element_class(driver, "field-username", msg)
    if field_username is None:
        msg += 'field_username not found in database'
        return False
    link_username = find_element_tag(field_username, "a", msg)
    if link_username is None:
        msg += "user not found in database"
        return False
    link_username.click()
    field_first_name = find_element_id(driver, "id_first_name", msg).get_attribute("value")
    field_last_name = find_element_id(driver, "id_last_name", msg).get_attribute("value")
    field_email = find_element_id(driver, "id_email", msg).get_attribute("value")
    if field_first_name != user.first_name or field_last_name != user.last_name or field_email != user.email:
        msg += "user information haven't saved correctly"
        return False
    return True
