from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from base.tests import BaseTestCase
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from .views import *

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
        self.driver.find_element(By.LINK_TEXT, "Registrarse").click()
        
        #Rellenar los campos
        self.driver.find_element(By.ID, "id_username").send_keys("Voter1")
        self.driver.find_element(By.ID, "id_password1").send_keys("Password 1")
        self.driver.find_element(By.ID, "id_password2").send_keys("Password 1")
        self.driver.find_element(By.ID, "id_email").send_keys("voter1@gmail.com")
        self.driver.find_element(By.ID, "id_age").send_keys("18")
        self.driver.find_element(By.ID, "id_country").send_keys("Spain")
        self.driver.find_element(By.XPATH, "/html/body/div/form/button").click()

        #Comprobar redireccion y existencia del perfil 
        assert User.objects.get(username='Voter1').email == 'voter1@gmail.com'

class AuthPageTextCase(TestCase):
    def test_form_no_username(self):
        #username ,password1 , password2, email , sex , age , status ,country , discord_account
        form= PersonForm({'password1':'Probando189!','password2':'Probando189!','email':'prueba@decide.es','status':'soltero','sex':'hombre','country':'NZ','discord_account':'prueba#1111'})
        
        #form = register(data={'email':'prueba@decide.es','password':'password123','sexo':'mujer','edad':'20'})

        self.assertEquals(form.errors['username'], ["This field is required."])

    def test_form_no_status(self):
        #form = register(data={'username':'prueba','password':'password123','sexo':'mujer','edad':'20'})
        form= PersonForm({'username':'prueba','password1':'Probando189!','password2':'Probando189!','email':'prueba@decide.es','sex':'hombre','country':'NZ','discord_account':'prueba#1111'})

        self.assertEquals(form.errors['status'], ["This field is required."])

    def test_form_no_password1(self):
        #form = register(data={'email':'prueba@decide.es','username':'prueba','sexo':'mujer','edad':'20'})
        form= PersonForm({'username':'prueba','password2':'Probando189!','email':'prueba@decide.es','status':'soltero','sex':'hombre','country':'NZ','discord_account':'prueba#1111'})

        self.assertEquals(form.errors['password1'], ["This field is required."])

    def test_form_no_password2(self):
        #form = register(data={'email':'prueba@decide.es','username':'prueba','sexo':'mujer','edad':'20'})
        form= PersonForm({'username':'prueba','password1':'Probando189!','email':'prueba@decide.es','status':'soltero','sex':'hombre','country':'NZ','discord_account':'prueba#1111'})

        self.assertEquals(form.errors['password2'], ["This field is required."])

    def test_form_no_sex(self):
        #form = register(data={'email':'prueba@decide.es','password':'password123','username':'prueba','edad':'20'})
        form= PersonForm({'username':'prueba','password1':'Probando189!','email':'prueba@decide.es','status':'soltero','country':'NZ','discord_account':'prueba#1111'})


        self.assertEquals(form.errors['sex'], ["This field is required."])

    def test_form_no_country(self):
        #form = register(data={'username':'prueba','password':'password123','sexo':'mujer','edad':'20'})
        form= PersonForm({'username':'prueba','password1':'Probando189!','password2':'Probando189!','email':'prueba@decide.es','status':'soltero','sex':'hombre','discord_account':'prueba#1111'})

        self.assertEquals(form.errors['country'], ["This field is required."])



