import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods
from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption

class VotingTestView(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        q = Question(desc='Prueba para votacion publica')
        q.save()

        #Creamos respuestas
        opt = QuestionOption(question=q, option='option 1')
        opt2 = QuestionOption(question=q, option='option 2')
        opt3 = QuestionOption(question=q, option='option 3')
        opt4 = QuestionOption(question=q, option='option 4')
        opt5 = QuestionOption(question=q, option='option 5')
        opt.save()
        opt2.save()
        opt3.save()
        opt4.save()
        opt5.save()
        self.v1 = Voting(name='Votacion Publica', question=q, public=True)
        self.v2 = Voting(name='Votacion No Publica', question=q, public=False)
        self.v1.save()
        self.v2.save()

        super().setUp()
    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.q = None
        self.opt = None
        self.opt2 = None
        self.opt3 = None
        self.opt4 = None
        self.opt5 = None

        self.v1 = None
        self.v2 = None

        self.base.tearDown()

class VotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        #response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        #self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')

    def test_createPublicVoting(self):
        q = Question(desc='Prueba para votacion publica')
        q.save()

        #Creamos respuestas
        opt = QuestionOption(question=q, option='option 1')
        opt2 = QuestionOption(question=q, option='option 2')
        opt3 = QuestionOption(question=q, option='option 3')
        opt4 = QuestionOption(question=q, option='option 4')
        opt5 = QuestionOption(question=q, option='option 5')

        opt.save()
        opt2.save()
        opt3.save()
        opt4.save()
        opt5.save()

        v = Voting(name='Votacion Publica', question=q, public=True)
        v.save()

        self.assertTrue(Voting.objects.all().filter(public=True, name='Votacion Publica').exists())

    def test_createNoPublicVoting(self):
        q = Question(desc='Prueba para votacion publica')
        q.save()

        #Creamos respuestas
        opt = QuestionOption(question=q, option='option 1')
        opt2 = QuestionOption(question=q, option='option 2')
        opt3 = QuestionOption(question=q, option='option 3')
        opt4 = QuestionOption(question=q, option='option 4')
        opt5 = QuestionOption(question=q, option='option 5')

        opt.save()
        opt2.save()
        opt3.save()
        opt4.save()
        opt5.save()

        v = Voting(name='Votacion No Publica', question=q, public=False)
        v.save()

        self.assertTrue(len(Voting.objects.all().filter(public=False, name='Votacion No Publica'))==1)

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class ViewTestCase(StaticLiveServerTestCase):
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        self.q = Question(desc='test question')
        self.q.save()
        for i in range(5):
            self.opt = QuestionOption(question=self.q, option='option {}'.format(i+1))
            self.opt.save()
        self.v = Voting(name='test voting', question=self.q)
        self.v.save()

        self.voter = User(username='test_user')
        self.voter.save()

        self.census = Census(voting_id=self.v.id, voter_id=self.voter.id)
        self.census.save()

        self.q1 = Question(desc='Prueba para añadir a censo')
        self.q1.save()

        #Creamos respuestas
        self.opt = QuestionOption(question=self.q1, option='option 1')
        self.opt2 = QuestionOption(question=self.q1, option='option 2')
        self.opt3 = QuestionOption(question=self.q1, option='option 3')
        self.opt4 = QuestionOption(question=self.q1, option='option 4')
        self.opt5 = QuestionOption(question=self.q1, option='option 5')
        self.opt.save()
        self.opt2.save()
        self.opt3.save()
        self.opt4.save()
        self.opt5.save()

        self.v1 = Voting(name='Votacion Publica', question=self.q1, public=True)
        self.v1.save()

        self.v2 = Voting(name='Votacion De Prueba Publica', question=self.q1, public=True)
        self.v2.save()

        self.voter2 = User.objects.get(username='admin')
        self.voter2.save()

        self.census2 = Census(voting_id=self.v2.id, voter_id=self.voter2.id)
        self.census2.save()


        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)

        super().setUp()
            
    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.q = None
        self.opt = None
        self.v = None
        self.census = None
        self.voter = None

        self.q1 = None
        self.opt = None
        self.opt2 = None
        self.opt3 = None
        self.opt4 = None
        self.opt5 = None
        self.v1 = None
        self.census2 = None
        self.voter2 = None

        self.base.tearDown()

    def test_traduccion_de_ingles_a_español(self):

        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty", Keys.ENTER)
        self.driver.get(f'{self.live_server_url}/voting/listadoVotaciones')           
        dropdown = self.driver.find_element(By.ID, "select-trad")
        dropdown.find_element(By.XPATH, "//*[@id='select-trad']/option[3]").click()
        element = self.driver.find_element(By.ID, "select-trad")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "select-trad")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "select-trad")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "trad").click()
        self.assertEquals(self.driver.find_element(By.ID, "listPubVotings").text, "List of Public Votings")
