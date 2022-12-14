from django.utils import timezone
from django.conf import settings
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
from census.models import Census
from django.contrib.auth.models import User
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt

from base import mods
from selenium import webdriver
from selenium.webdriver.common.by import By
from .views import graphics, funcionLoser, funcionPorcentaje, funcionWinner

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
        for i in range(10):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_correct_access_graphics(self):
        v = Voting.objects.get(name='Helado')
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            pk = v.pub_key
            p, g, y = (pk.p, pk.g, pk.y)
            k = MixCrypt(bits=settings.KEYBITS)
            k.k = ElGamal.construct((p, g, y))
            a, b = k.encrypt(opt.number)
            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'vote': { 'a': a, 'b': b },
            }
            clear[opt.number] += 1
            user, _ = User.objects.get_or_create(pk=voter.voter_id)
            user.username = 'user{}'.format(voter.voter_id)
            user.set_password('qwerty')
            user.save()
            self.login(user=user.username)
            voter = voters.pop()
            mods.post('store', json=data)
        self.login()  # set token
        v.tally_votes(self.token)
        #Se comprueba que se puede acceder a las gráficas de dicha votación
        request = self.client.post('/graphics/{}'.format(v.pk), format='json')
        response = graphics(request, voting_id=v.id)
        self.assertEquals(response.status_code,200)

    def test_graphic_template_correct(self):
        v = Voting.objects.get(name='Helado')
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            pk = v.pub_key
            p, g, y = (pk.p, pk.g, pk.y)
            k = MixCrypt(bits=settings.KEYBITS)
            k.k = ElGamal.construct((p, g, y))
            a, b = k.encrypt(opt.number)
            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'vote': { 'a': a, 'b': b },
            }
            clear[opt.number] += 1
            user, _ = User.objects.get_or_create(pk=voter.voter_id)
            user.username = 'user{}'.format(voter.voter_id)
            user.set_password('qwerty')
            user.save()
            self.login(user=user.username)
            voter = voters.pop()
            mods.post('store', json=data)
        self.login()  # set token
        v.tally_votes(self.token)
        #Se comprueba que se carga el template de graphics correctamente
        response = self.client.post('/graphics/{}'.format(v.pk), format='json')
        self.assertTemplateUsed(response, "graphics.html")

    def test_winner_option(self):
        v = Voting.objects.get(name='Helado')
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = {}
        i = 0
        for opt in v.question.options.all():
            if opt.number == 0:
                while i < 5:
                    clear[opt.number] = 0
                    pk = v.pub_key
                    p, g, y = (pk.p, pk.g, pk.y)
                    k = MixCrypt(bits=settings.KEYBITS)
                    k.k = ElGamal.construct((p, g, y))
                    a, b = k.encrypt(opt.number)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user, _ = User.objects.get_or_create(pk=voter.voter_id)
                    user.username = 'user{}'.format(voter.voter_id)
                    user.set_password('qwerty')
                    user.save()
                    self.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
                    i+=1
            else:
                clear[opt.number] = 0
                pk = v.pub_key
                p, g, y = (pk.p, pk.g, pk.y)
                k = MixCrypt(bits=settings.KEYBITS)
                k.k = ElGamal.construct((p, g, y))
                a, b = k.encrypt(opt.number)
                data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user, _ = User.objects.get_or_create(pk=voter.voter_id)
                user.username = 'user{}'.format(voter.voter_id)
                user.set_password('qwerty')
                user.save()
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
            self.login()  # set token
            v.tally_votes(self.token)
            #Se comprueba que la opción más votada es Chocolate
            self.assertEquals(funcionWinner(voting_id=v.id)['option'], 'Chocolate')

    def test_loser_option(self):
        v = Voting.objects.get(name='Helado')
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = {}
        i = 0
        for opt in v.question.options.all():
            if opt.number == 0:
                while i < 5:
                    clear[opt.number] = 0
                    pk = v.pub_key
                    p, g, y = (pk.p, pk.g, pk.y)
                    k = MixCrypt(bits=settings.KEYBITS)
                    k.k = ElGamal.construct((p, g, y))
                    a, b = k.encrypt(opt.number)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user, _ = User.objects.get_or_create(pk=voter.voter_id)
                    user.username = 'user{}'.format(voter.voter_id)
                    user.set_password('qwerty')
                    user.save()
                    self.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
                    i+=1
            elif opt.number == 2:
                while i < 2:
                    clear[opt.number] = 0
                    pk = v.pub_key
                    p, g, y = (pk.p, pk.g, pk.y)
                    k = MixCrypt(bits=settings.KEYBITS)
                    k.k = ElGamal.construct((p, g, y))
                    a, b = k.encrypt(opt.number)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user, _ = User.objects.get_or_create(pk=voter.voter_id)
                    user.username = 'user{}'.format(voter.voter_id)
                    user.set_password('qwerty')
                    user.save()
                    self.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
                    i+=1
            self.login()  # set token
            v.tally_votes(self.token)
            #Se comprueba que la opción menos votada es Vainilla
            self.assertEquals(funcionLoser(voting_id=v.id)['option'], 'Vainilla')

    def test_options_percentage(self):
        v = Voting.objects.get(name='Helado')
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            pk = v.pub_key
            p, g, y = (pk.p, pk.g, pk.y)
            k = MixCrypt(bits=settings.KEYBITS)
            k.k = ElGamal.construct((p, g, y))
            a, b = k.encrypt(opt.number)
            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'vote': { 'a': a, 'b': b },
            }
            clear[opt.number] += 1
            user, _ = User.objects.get_or_create(pk=voter.voter_id)
            user.username = 'user{}'.format(voter.voter_id)
            user.set_password('qwerty')
            user.save()
            self.login(user=user.username)
            voter = voters.pop()
            mods.post('store', json=data)
        self.login()  # set token
        v.tally_votes(self.token)
        #Se comprueba que la opción más votada es Chocolate
        response = funcionPorcentaje(voting_id=v.id)
        self.assertEquals(response, [33, 33, 33])

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
        #Creamos usuarios para la votación
        for i in range(10):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def test_exist_graphics(self):
        v = Voting.objects.get(name='Helado')
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            pk = v.pub_key
            p, g, y = (pk.p, pk.g, pk.y)
            k = MixCrypt(bits=settings.KEYBITS)
            k.k = ElGamal.construct((p, g, y))
            a, b = k.encrypt(opt.number)
            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'vote': { 'a': a, 'b': b },
            }
            clear[opt.number] += 1
            user, _ = User.objects.get_or_create(pk=voter.voter_id)
            user.username = 'user{}'.format(voter.voter_id)
            user.set_password('qwerty')
            user.save()
            self.base.login(user=user.username)
            voter = voters.pop()
            mods.post('store', json=data)
        self.base.login()
        v.tally_votes(self.base.token)
        self.driver.get('{}/graphics/{}'.format(self.live_server_url, v.pk))
        tituloPag = self.driver.find_element(By.XPATH, '//div[@class="logo"]').text
        graficaBarras = self.driver.find_elements(By.ID, 'grafic')
        graficaPie = self.driver.find_elements(By.ID, 'grafica')
        self.assertTrue(len(graficaBarras)==1)
        self.assertTrue(len(graficaPie)==1)
        self.assertEquals(tituloPag, "Votaciones para 'Helado'")

    def test_winner_option_exist(self):
        v = Voting.objects.get(name='Helado')
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = {}
        i = 0
        for opt in v.question.options.all():
            if opt.number == 0:
                while i < 5:
                    clear[opt.number] = 0
                    pk = v.pub_key
                    p, g, y = (pk.p, pk.g, pk.y)
                    k = MixCrypt(bits=settings.KEYBITS)
                    k.k = ElGamal.construct((p, g, y))
                    a, b = k.encrypt(opt.number)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user, _ = User.objects.get_or_create(pk=voter.voter_id)
                    user.username = 'user{}'.format(voter.voter_id)
                    user.set_password('qwerty')
                    user.save()
                    self.base.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
                    i+=1
            elif opt.number == 2:
                while i < 2:
                    clear[opt.number] = 0
                    pk = v.pub_key
                    p, g, y = (pk.p, pk.g, pk.y)
                    k = MixCrypt(bits=settings.KEYBITS)
                    k.k = ElGamal.construct((p, g, y))
                    a, b = k.encrypt(opt.number)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user, _ = User.objects.get_or_create(pk=voter.voter_id)
                    user.username = 'user{}'.format(voter.voter_id)
                    user.set_password('qwerty')
                    user.save()
                    self.base.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
                    i+=1
            self.base.login()  # set token
            v.tally_votes(self.base.token)
            #Se comprueba que la opción más votada es Chocolate
            self.driver.get('{}/graphics/{}'.format(self.live_server_url, v.pk))
            ganador = self.driver.find_element(By.ID, 'winner').text
            self.assertEquals(ganador, 'El voto ganador es "Chocolate"')

    def test_loser_option_exist(self):
        v = Voting.objects.get(name='Helado')
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = {}
        i = 0
        for opt in v.question.options.all():
            if opt.number == 0:
                while i < 5:
                    clear[opt.number] = 0
                    pk = v.pub_key
                    p, g, y = (pk.p, pk.g, pk.y)
                    k = MixCrypt(bits=settings.KEYBITS)
                    k.k = ElGamal.construct((p, g, y))
                    a, b = k.encrypt(opt.number)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user, _ = User.objects.get_or_create(pk=voter.voter_id)
                    user.username = 'user{}'.format(voter.voter_id)
                    user.set_password('qwerty')
                    user.save()
                    self.base.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
                    i+=1
            elif opt.number == 2:
                while i < 2:
                    clear[opt.number] = 0
                    pk = v.pub_key
                    p, g, y = (pk.p, pk.g, pk.y)
                    k = MixCrypt(bits=settings.KEYBITS)
                    k.k = ElGamal.construct((p, g, y))
                    a, b = k.encrypt(opt.number)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user, _ = User.objects.get_or_create(pk=voter.voter_id)
                    user.username = 'user{}'.format(voter.voter_id)
                    user.set_password('qwerty')
                    user.save()
                    self.base.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
                    i+=1
            self.base.login()  # set token
            v.tally_votes(self.base.token)
            #Se comprueba que la opción más votada es Chocolate
            self.driver.get('{}/graphics/{}'.format(self.live_server_url, v.pk))
            ganador = self.driver.find_element(By.ID, 'loser').text
            self.assertEquals(ganador, 'El voto perdedor es "Vainilla"')