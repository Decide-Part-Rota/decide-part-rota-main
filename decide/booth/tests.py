from base import mods
from base.tests import BaseTestCase

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from rest_framework.test import APIClient

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from unittest import skip

import time 

class BoothTestCases(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        #Si se quieren ver en navegador, cambiar a false
        options.headless = False

        self.driver = webdriver.Chrome(options=options) 

        super().setUp() 


    def tearDown(self):
        super().tearDown() 
        self.driver.quit() 
        self.base.tearDown()
    
    def test_join_voting_sign_in(self):
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8000/booth/2/') 
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys("pruebas")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys("pruebaspruebas")
        self.driver.find_element(By.XPATH, "//*[@id='app-booth']/div/div[3]/form/button").click()
        time.sleep(0.5)

        self.assertTrue("2  -  Qué hora es" in self.driver.page_source)

    def test_join_voting_without_sign_in(self):
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8000/booth/2/') 
        self.assertTrue("2  -  Qué hora es" in self.driver.page_source)


