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
        options.headless = True

        self.driver = webdriver.Chrome(options=options) 

        super().setUp()

    def tearDown(self):
        super().tearDown() 
        self.driver.quit() 
        self.base.tearDown()

    
    def test_join_voting_without_sign_in_succesful_id_name_appear(self):
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8000/booth/2/') 
        self.assertTrue("2  -  Qué hora es" in self.driver.page_source)

    def test_join_voting_without_sign_in_succesful_desc_appear(self):
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8000/booth/2/') 
        self.assertTrue("¿Cuál es la hora actual? Indícalo:" in self.driver.page_source)


    def test_logout_button_works(self):
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8000/booth/2/') 
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys("pruebas")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys("pruebaspruebas")
        self.driver.find_element(By.XPATH, "//*[@id='app-booth']/div/div[3]/form/button").click()
        time.sleep(0.5)

        self.driver.find_element(By.XPATH, "//*[@id='app-booth']/nav/ul/li/a").click()

        self.assertTrue("Username" in self.driver.page_source)



    def test_voting_without_choosing_option_raises_error(self):
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8000/booth/2/') 
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys("pruebas")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys("pruebaspruebas")
        self.driver.find_element(By.XPATH, "//*[@id='app-booth']/div/div[3]/form/button").click()
        time.sleep(0.5)

        ##If we dont choose any option, voting will not finish
        self.driver.find_element(By.XPATH, "//*[@id='app-booth']/div/div[3]/div/button").click
        time.sleep(0.5)
        self.assertFalse("            Conglatulations. Your vote has been sent        " in self.driver.page_source)


    def test_voting_different_works(self):
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8000/booth/1/') 
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys("decide")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys("Javier111")
        self.driver.find_element(By.XPATH, "//*[@id='app-booth']/div/div[3]/form/button").click()
        time.sleep(0.5)
        time.sleep(0.5)
        self.assertTrue("1  -  Fecha de hoy" in self.driver.page_source)

    def test_voting(self):
        self.driver.maximize_window()
        self.driver.get('http://127.0.0.1:8000/booth/1/') 
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys("decide")
        time.sleep(0.5)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys("Javier111")
        time.sleep(0.5)




        self.assertTrue("Elige cual es la fecha de hoy" in self.driver.page_source)







    


