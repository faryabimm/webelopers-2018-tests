from selenium import webdriver
import utils as ut


sharif_ip = 'http://192.168.192.114:8000'
global_ip = 'http://81.31.175.72:8000'

driver = webdriver.Chrome()


def test_1():
    navbar = ut.find_element(driver, "navbar", driver)
    navbar_login = ut.find_element(navbar, "navbar_login", driver)
    navbar_signup = ut.find_element(navbar, "navbar_signup", driver)
    navbar_home = ut.find_element(navbar, "navbar_home", driver)
    welcome = ut.find_element(driver, "welcome", driver)
    if welcome.text != "به سامانه استاد جو خوش آمدید.":
        print("incorrect welcome message")
        driver.close()
        exit(1)
    home_url = driver.current_url
    home_source = driver.page_source
    navbar_home.click()
    if driver.current_url != home_url or driver.page_source != home_source:
        print("home button doesn't work")
        driver.close()
        exit(1)
    exit(0)


def test_2():



ut.connect(sharif_ip, driver)
test_1()
driver.close()
