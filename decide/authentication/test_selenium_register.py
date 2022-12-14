from base.tests import BaseTestCase

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

import time

class RegisterTestCase(StaticLiveServerTestCase):
      
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        #Si se quieren ver en navegador, cambiar a false
        options.headless = True
        self.driver = webdriver.Chrome(options=options) 
    
    def tearDown(self):
        super().tearDown() 
        self.driver.quit() 
        self.base.tearDown() 

    def test_register_ok(self):
        self.driver.maximize_window()
        self.driver.get(''f'{self.live_server_url}''/authentication/registerForm/')

        self.driver.find_element(By.ID, "id_username").clear()
        self.driver.find_element(By.ID, "id_username").send_keys("user")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_password1").clear()
        self.driver.find_element(By.ID, "id_password1").send_keys("12user34")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_password2").clear()
        self.driver.find_element(By.ID, "id_password2").send_keys("12user34")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_email").clear()
        self.driver.find_element(By.ID, "id_email").send_keys("user@user.com")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_sex").find_element(By.XPATH, "//option[. = 'Hombre']").click()
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_age").clear()
        self.driver.find_element(By.ID, "id_age").send_keys("34")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_status").find_element(By.XPATH, "//option[. = 'Conviviente']").click()
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_country").find_element(By.XPATH, "//option[. = 'Azerbaijan']").click()
        time.sleep(0.5)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(0.5)

        self.assertTrue("Inicia sesión" in self.driver.page_source)

    def test_register_fail_username_wrong_character(self):
        self.driver.maximize_window()
        self.driver.get(''f'{self.live_server_url}''/authentication/registerForm/')

        self.driver.find_element(By.ID, "id_username").clear()
        self.driver.find_element(By.ID, "id_username").send_keys("user,")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_password1").clear()
        self.driver.find_element(By.ID, "id_password1").send_keys("12user34")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_password2").clear()
        self.driver.find_element(By.ID, "id_password2").send_keys("12user34")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_email").clear()
        self.driver.find_element(By.ID, "id_email").send_keys("user@user.com")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_sex").find_element(By.XPATH, "//option[. = 'Hombre']").click()
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_age").clear()
        self.driver.find_element(By.ID, "id_age").send_keys("34")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_status").find_element(By.XPATH, "//option[. = 'Conviviente']").click()
        time.sleep(0.5)
        self.driver.find_element(By.ID, "id_country").find_element(By.XPATH, "//option[. = 'Azerbaijan']").click()
        time.sleep(0.5)
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(0.5)

        self.assertTrue("Registro" in self.driver.page_source)