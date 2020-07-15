import requests
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

url_login = 'https://app.inventorysource.com/#/login'
url_products = 'https://app.inventorysource.com/#/products/'
login_email = 'rmaluski@comcast.net'
login_password = 'Upwork1'


class Scraper:
    """Product Scraper class
    """

    def __init__(self):
        self.should_stop = False
        self.driver = webdriver.Chrome()
        self.driver.wait = WebDriverWait(self.driver, 5)

    def run(self):
        self.should_stop = False
        self.login()
        self.apply_filter()

    def stop(self):
        self.should_stop = True

    def login(self):
        self.driver.get(url_login)
        input_email = self.driver.find_element_by_name('email')
        input_password = self.driver.find_element_by_name('password')
        btn_login = self.driver.find_element_by_css_selector('button[type="submit"]')
        input_email.send_keys(login_email)
        input_password.send_keys(login_password)
        btn_login.click()

    def apply_filter(self):
        script = '$(".sidebar-col .options div:nth-child(3) .dropdown-menu div:nth-child(6)").click();' \
                 '$(".sidebar-col .text-right div.btn.btn-lg.btn-primary").click();'
        self.driver.get(url_products)
        time.sleep(10)
        self.driver.execute_script(script)
        time.sleep(10)



