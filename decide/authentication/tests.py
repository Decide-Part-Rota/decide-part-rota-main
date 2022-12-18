from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from authentication.models import Person
from rest_framework.authtoken.models import Token

from base import mods

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from base.tests import BaseTestCase
from authentication.forms import CompleteForm
import time

class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username='voter1', email="voter1@gmail.com")
        u.set_password('123')

        u.save()

        

        u2 = User(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        self.client = None

    def test_login(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 1)
        self.assertEqual(user['username'], 'voter1')

    def test_getuser_invented_token(self):
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    def test_register_bad_permissions(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 401)

    def test_register_bad_request(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_user_already_exist(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update(data)
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1', 'password': 'pwd1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            sorted(list(response.json().keys())),
            ['token', 'user_pk']
        )


    # Tests anhadidos

    def test_login_with_email(self):
        data = {'username': 'voter1@gmail.com', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_with_email_fail(self):
        data = {'username': 'voter1@gmail.com', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_logout_with_email(self):
        data = {'username': 'voter1@gmail.com', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    def test_getuser_with_email(self):
        data = {'username': 'voter1@gmail.com', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 7)
        self.assertEqual(user['username'], 'voter1')


class CompleteUnitTestCase(APITestCase):
    def test_unitCorrectComplete(self):
        form_data = {
            'sex': 'hombre',
            'age': '20',
            'status': 'soltero',
            'discord_account': 'name#0123',
            'country': "AD"
            }

        form = CompleteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_unitIncorrectSexComplete(self):
        form_data = {
            'sex': 'ninguno',
            'age': '20',
            'status': 'soltero',
            'discord_account': 'name#0123',
            'country': "AD"
            }

        form = CompleteForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_unitIncorrectAgeComplete(self):
        form_data = {
            'sex': 'hombre',
            'age': '-10',
            'status': 'soltero',
            'discord_account': 'name#0123',
            'country': "AD"
            }

        form = CompleteForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_unitIncorrectAgeComplete2(self):
        form_data = {
            'sex': 'hombre',
            'age': '0',
            'status': 'soltero',
            'discord_account': 'name#0123',
            'country': "AD"
            }

        form = CompleteForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_unitIncorrectStatusComplete(self):
        form_data = {
            'sex': 'hombre',
            'age': '20',
            'status': 'a dos velas',
            'discord_account': 'name#0123',
            'country': "AD"
            }

        form = CompleteForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_unitIncorrectDiscordAccountComplete(self):
        form_data = {
            'sex': 'hombre',
            'age': '20',
            'status': 'soltero',
            'discord_account': 'name#012',
            'country': "AD"
            }

        form = CompleteForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_unitIncorrectCountryComplete(self):
        form_data = {
            'sex': 'hombre',
            'age': '20',
            'status': 'soltero',
            'discord_account': 'name#0123',
            'country': "ZZ"
            }

        form = CompleteForm(data=form_data)
        self.assertFalse(form.is_valid())


class RegisterTestCase(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()


    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()


    def test_simpleCorrectRegister(self):
        self.driver.get(f'{self.live_server_url}/authentication/registerForm/')
        self.driver.find_element(By.ID,'id_username').send_keys("test1")
        self.driver.find_element(By.ID,'id_password1').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_password2').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_email').send_keys("test1@yopmail.com")
        self.driver.find_element(By.ID,'id_sex').send_keys("Mujer")
        self.driver.find_element(By.ID,'id_age').send_keys("20")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        # time.sleep(10)

        print(self.live_server_url)

        self.assertEqual(self.driver.title, 'Login')

    def test_simpleIncorrectPasswordRegister(self):
        self.driver.get(f'{self.live_server_url}/authentication/registerForm/')
        self.driver.find_element(By.ID,'id_username').send_keys("test1")
        self.driver.find_element(By.ID,'id_password1').send_keys("complexpassword")

        # Probar un registro con una contrasenya que no coincide
        
        self.driver.find_element(By.ID,'id_password2').send_keys("complexpassword2")
        self.driver.find_element(By.ID,'id_email').send_keys("test1@yopmail.com")
        self.driver.find_element(By.ID,'id_sex').send_keys("Mujer")
        self.driver.find_element(By.ID,'id_age').send_keys("20")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        print(self.live_server_url)

        self.assertEqual(self.driver.title, 'Register')

    
    def test_simpleIncorrectAgeRegister(self): 
        self.driver.get(f'{self.live_server_url}/authentication/registerForm/')
        self.driver.find_element(By.ID,'id_username').send_keys("test1")
        self.driver.find_element(By.ID,'id_password1').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_password2').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_email').send_keys("test1@yopmail.com")
        self.driver.find_element(By.ID,'id_sex').send_keys("Mujer")

        # Probar un register con una edad invalida

        self.driver.find_element(By.ID,'id_age').send_keys("0")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        print(self.live_server_url)

        self.assertEqual(self.driver.title, 'Register')

    def test_simpleIncorrectSexRegister(self): 
        self.driver.get(f'{self.live_server_url}/authentication/registerForm/')
        self.driver.find_element(By.ID,'id_username').send_keys("test1")
        self.driver.find_element(By.ID,'id_password1').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_password2').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_email').send_keys("test1@yopmail.com")
        # Probar un register con sexo invalido
        self.driver.find_element(By.ID,'id_sex').send_keys("Helicoptero")
        self.driver.find_element(By.ID,'id_age').send_keys("1")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        print(self.live_server_url)

        self.assertEqual(self.driver.title, 'Login')

    def test_simpleIncorrectStatusRegister(self): 
        self.driver.get(f'{self.live_server_url}/authentication/registerForm/')
        self.driver.find_element(By.ID,'id_username').send_keys("test1")
        self.driver.find_element(By.ID,'id_password1').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_password2').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_email').send_keys("test1@yopmail.com")
        self.driver.find_element(By.ID,'id_sex').send_keys("Mujer")
        self.driver.find_element(By.ID,'id_age').send_keys("1")
        # Probar un register con estado invalida
        self.driver.find_element(By.ID,'id_status').send_keys("Con novia")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        print(self.live_server_url)

        self.assertEqual(self.driver.title, 'Login')

    def test_simpleIncorrectCountryRegister(self): 
        self.driver.get(f'{self.live_server_url}/authentication/registerForm/')
        self.driver.find_element(By.ID,'id_username').send_keys("test1")
        self.driver.find_element(By.ID,'id_password1').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_password2').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_email').send_keys("test1@yopmail.com")
        self.driver.find_element(By.ID,'id_sex').send_keys("Mujer")
        self.driver.find_element(By.ID,'id_age').send_keys("1")
        self.driver.find_element(By.ID,'id_status').send_keys("Con novia")
        # Probar un register con pais invalido
        self.driver.find_element(By.ID,'id_country').send_keys("Mi casa")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        print(self.live_server_url)

        self.assertEqual(self.driver.title, 'Login')

    def test_simpleIncorrectMailRegister(self): 
        self.driver.get(f'{self.live_server_url}/authentication/registerForm/')
        self.driver.find_element(By.ID,'id_username').send_keys("test1")
        self.driver.find_element(By.ID,'id_password1').send_keys("complexpassword")
        self.driver.find_element(By.ID,'id_password2').send_keys("complexpassword")
        # Probar un register con mail invalido
        self.driver.find_element(By.ID,'id_email').send_keys("miEmail")
        self.driver.find_element(By.ID,'id_sex').send_keys("Mujer")
        self.driver.find_element(By.ID,'id_age').send_keys("1")
        self.driver.find_element(By.ID,'id_status').send_keys("Con novia")
        self.driver.find_element(By.ID,'id_country').send_keys("Sevilla")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        print(self.live_server_url)

        self.assertEqual(self.driver.title, 'Register')


class CompleteTestCase(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        u = User(username='voter1', email="voter1@gmail.com")
        u.set_password('123')
        u.save()

        p = Person.objects.filter(user=User.objects.get(username='voter1'))
        if p.exists():
            p[0].delete()

        super().setUp()


    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()


    def test_user_without_person(self):
        self.driver.get(f'{self.live_server_url}/authentication/accounts/login/')
        self.driver.find_element(By.ID,'id_username').send_keys("voter1")
        self.driver.find_element(By.ID,'id_password').send_keys("123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/authentication/completeForm/')
        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Complete')

    def test_user_with_person(self):
        self.driver.get(f'{self.live_server_url}/authentication/accounts/login/')
        self.driver.find_element(By.ID,'id_username').send_keys("voter1")
        self.driver.find_element(By.ID,'id_password').send_keys("123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/authentication/completeForm/')
        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Complete')

        self.driver.find_element(By.ID,'id_sex').send_keys("Hombre")
        self.driver.find_element(By.ID,'id_age').send_keys("20")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_discord_account').send_keys("name#0123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Inicio')
        
        self.driver.get(f'{self.live_server_url}/authentication/completeForm/')
        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Inicio')


    def test_simpleCorrectComplete(self):
        self.driver.get(f'{self.live_server_url}/authentication/accounts/login/')
        self.driver.find_element(By.ID,'id_username').send_keys("voter1")
        self.driver.find_element(By.ID,'id_password').send_keys("123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/authentication/completeForm/')
        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Complete')

        self.driver.find_element(By.ID,'id_sex').send_keys("Hombre")
        self.driver.find_element(By.ID,'id_age').send_keys("20")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_discord_account').send_keys("name#0123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Inicio')

    def test_simpleIncorrectSexComplete(self):
        self.driver.get(f'{self.live_server_url}/authentication/accounts/login/')
        self.driver.find_element(By.ID,'id_username').send_keys("voter1")
        self.driver.find_element(By.ID,'id_password').send_keys("123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/authentication/completeForm/')
        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Complete')
        # Probar un complete con sexo invalido
        self.driver.find_element(By.ID,'id_sex').send_keys("Helicoptero")
        self.driver.find_element(By.ID,'id_age').send_keys("0")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_discord_account').send_keys("name#0123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        print(self.live_server_url)

        self.assertEqual(self.driver.title, 'Complete')

    def test_simpleIncorrectAgeComplete(self):
        self.driver.get(f'{self.live_server_url}/authentication/accounts/login/')
        self.driver.find_element(By.ID,'id_username').send_keys("voter1")
        self.driver.find_element(By.ID,'id_password').send_keys("123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/authentication/completeForm/')
        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Complete')

        self.driver.find_element(By.ID,'id_sex').send_keys("Hombre")
        # Probar un complete con una edad invalida
        self.driver.find_element(By.ID,'id_age').send_keys("0")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_discord_account').send_keys("name#0123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)


        print(self.live_server_url)

        self.assertEqual(self.driver.title, 'Complete')

    def test_simpleIncorrectStatusComplete(self):
        self.driver.get(f'{self.live_server_url}/authentication/accounts/login/')
        self.driver.find_element(By.ID,'id_username').send_keys("voter1")
        self.driver.find_element(By.ID,'id_password').send_keys("123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/authentication/completeForm/')
        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Complete')

        self.driver.find_element(By.ID,'id_sex').send_keys("Hombre")
        self.driver.find_element(By.ID,'id_age').send_keys("0")
        # Probar un complete con estado invalido
        self.driver.find_element(By.ID,'id_status').send_keys("A dos velas")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        self.driver.find_element(By.ID,'id_discord_account').send_keys("name#0123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        self.assertEqual(self.driver.title, 'Complete')
    
    def test_simpleIncorrectCountryComplete(self):
        self.driver.get(f'{self.live_server_url}/authentication/accounts/login/')
        self.driver.find_element(By.ID,'id_username').send_keys("voter1")
        self.driver.find_element(By.ID,'id_password').send_keys("123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/authentication/completeForm/')
        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Complete')

        self.driver.find_element(By.ID,'id_sex').send_keys("Hombre")
        self.driver.find_element(By.ID,'id_age').send_keys("0")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        # Probar un complete con pais invalido
        self.driver.find_element(By.ID,'id_country').send_keys("Sevilla")
        self.driver.find_element(By.ID,'id_discord_account').send_keys("name#0123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        self.assertEqual(self.driver.title, 'Complete')

    def test_simpleIncorrectDiscordAccountComplete(self):
        self.driver.get(f'{self.live_server_url}/authentication/accounts/login/')
        self.driver.find_element(By.ID,'id_username').send_keys("voter1")
        self.driver.find_element(By.ID,'id_password').send_keys("123")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)
        
        self.driver.get(f'{self.live_server_url}/authentication/completeForm/')
        print(self.live_server_url)
        self.assertEqual(self.driver.title, 'Complete')

        self.driver.find_element(By.ID,'id_sex').send_keys("Hombre")
        self.driver.find_element(By.ID,'id_age').send_keys("20")
        self.driver.find_element(By.ID,'id_status').send_keys("Soltero")
        self.driver.find_element(By.ID,'id_country').send_keys("Andorra")
        # Probar un complete con cuenta de discord invalida
        self.driver.find_element(By.ID,'id_discord_account').send_keys("name#012")
        self.driver.find_element(By.ID,'id_button').send_keys(Keys.ENTER)

        self.assertEqual(self.driver.title, 'Complete')
