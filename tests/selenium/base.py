import os
import unittest


try:
    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError:
    webdriver = None
    WebDriverException = None
    By = None
    Keys = None
    EC = None
    WebDriverWait = None


RUN_SELENIUM = os.environ.get("RUN_SELENIUM") == "1"
BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:5000")


@unittest.skipUnless(RUN_SELENIUM, "Set RUN_SELENIUM=1 to run Selenium tests.")
@unittest.skipIf(webdriver is None, "Install selenium to run Selenium tests.")
class SeleniumTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()

        if os.environ.get("SELENIUM_HEADLESS", "1") == "1":
            options.add_argument("--headless=new")

        options.add_argument("--window-size=1280,900")

        try:
            cls.driver = webdriver.Chrome(options=options)
        except WebDriverException as error:
            raise unittest.SkipTest(f"Chrome WebDriver is unavailable: {error}")

        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def open_path(self, path):
        self.driver.get(BASE_URL + path)

    def login_as_seed_customer(self):
        self.open_path("/login")
        self.wait.until(EC.presence_of_element_located((By.ID, "emailInput"))).send_keys(
            "customer01@example.com"
        )
        self.driver.find_element(By.ID, "passwordInput").send_keys("password")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(EC.url_contains("/restaurants/1"))
