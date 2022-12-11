from django.utils import timezone
from django.conf import settings
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
from census.models import Census
from django.contrib.auth.models import User

from selenium import webdriver
from selenium.webdriver.common.by import By


# Create your tests here.

class GraphicsTestCases(BaseTestCase):
    def setUp(self):
        #Creamos votación
        q = Question(desc='Tipos de helados')
        q.save()
        opt1 = QuestionOption(question=q, option='Chocolate')
        opt1.save()
        opt2 = QuestionOption(question=q, option='Vainilla')
        opt2.save()
        opt3 = QuestionOption(question=q, option='Frambuesa')
        opt3.save()

        v = Voting(name='Helado', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        #Creamos usuarios para la votación
        for i in range(25):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()
        
        user, _ = User.objects.get_or_create(pk=v.pk)
        user.username = 'user{}'.format(v.pk)
        user.set_password('qwerty')
        user.save()

        super().setUp()
    
    def tearDown(self):
        super().tearDown()

    def test_correct_access_graphics(self):
        v = Voting.objects.get(name='Helado')
        v.start_date = timezone.now()
        v.save()

        self.login()  # set token
        v.tally_votes(self.token)

        #Se comprueba que se puede acceder a las gráficas de dicha votación
        response = self.client.post('/graphics/{}'.format(v.pk), format='json')
        self.assertEquals(response.status_code,200)

    def test_graphic_template_correct(self):
        v = Voting.objects.get(name='Helado')

        v.start_date = timezone.now()
        v.save()

        self.login()  # set token
        v.tally_votes(self.token)


        #Se comprueba que el template se cargó correctamente
        response = self.client.post('/graphics/{}'.format(v.pk), format='json')
        self.assertTemplateUsed(response, "graphics.html")
    
class SeleniumGraphics(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        q = Question(desc='Tipos de helados')
        q.save()
        opt1 = QuestionOption(question=q, option='Chocolate')
        opt1.save()
        opt2 = QuestionOption(question=q, option='Vainilla')
        opt2.save()
        opt3 = QuestionOption(question=q, option='Frambuesa')
        opt3.save()

        v = Voting(name='Helado', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_exist_graphic_bars(self):
        v = Voting.objects.get(name='Helado')

        self.driver.get('{}/graphics/{}'.format(self.live_server_url, v.pk))
        tituloPag = self.driver.find_element(By.XPATH, '//div[@class="logo"]').text
        graficaBarras = self.driver.find_elements(By.ID, 'grafic')
        self.assertTrue(len(graficaBarras)==1)
        self.assertEquals(tituloPag, "Votaciones para 'Helado'")



   
    
    
