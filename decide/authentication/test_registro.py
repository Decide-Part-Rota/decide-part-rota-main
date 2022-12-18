from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from base.tests import BaseTestCase
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User

class testRegistro(StaticLiveServerTestCase):
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
    
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def testRegistroCorrecto(self):
        #Crear server
        self.driver.get(f'{self.live_server_url}')
        self.driver.set_window_size(1366, 728)

        #Clickar en registrarse
        self.driver.find_element(By.ID, "button_registrar").click()
        
        #Rellenar los campos
        self.driver.find_element(By.ID, "id_username").send_keys("Voter1")
        self.driver.find_element(By.ID, "id_password1").send_keys("Password 1")
        self.driver.find_element(By.ID, "id_password2").send_keys("Password 1")
        self.driver.find_element(By.ID, "id_email").send_keys("voter1@gmail.com")
        self.driver.find_element(By.ID, "id_age").send_keys("18")
        self.driver.find_element(By.ID, "id_country").send_keys("Spain")
        self.driver.find_element(By.XPATH, "/html/body/div/form/button").click()

        #Comprobar redireccion y existencia del perfil
        boton = self.driver.find_elements(By.ID, "button_registrar")
        assert len(boton) == 1
        assert User.objects.get(username='Voter1').email == 'voter1@gmail.com'
