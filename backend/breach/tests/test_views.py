from django.test import Client, TestCase
from django.core.urlresolvers import reverse
from breach.models.victim import Victim
from breach.models.target import Target
from breach.models.round import Round
from breach.models.sampleset import SampleSet
from breach.views import victim, target
import json

from binascii import hexlify


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_victimID_get(self):

        target_data = {
            'name': 'ruptureit',
            'endpoint': 'https://ruptureit.com/test.php?reflection=%s',
            'prefix': 'imper',
            'alphabet': 'abcdefghijklmnopqrstuvwxyz',
            'secretlength': 9,
            'alignmentalphabet': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'recordscardinality': 1,
            'method': 'serial'
        }

        target = Target.create_target(target_data)

        victim_data = {
            'sourceip': '192.168.1.5',
            'target': target
        }
        victim = Victim.create_victim(victim_data)

        victim2_data = {
            'sourceip': '192.168.1.6',
            'target': target
        }
        victim2 = Victim.create_victim(victim2_data)

        round_data = {
            'victim': victim,
            'index': 1,
            'amount': target.samplesize,
            'knownalphabet': 'abcdefghijklmnopqrstuvxyz',
            'knownsecret': 'imper'
        }
        new_round = Round(**round_data)
        new_round.save()

        sampleset1_data = {
                'round': new_round,
                'candidatealphabet': 'a',
                'data': hexlify('length'),
                'success': True,
                'alignmentalphabet': 'ABCDEFGHIJKLMNOPQRSTUVXYZ'
        }
        sampleset = SampleSet(**sampleset1_data)
        sampleset.save()

        sampleset2_data = {
                'round': new_round,
                'candidatealphabet': 'b',
                'data': hexlify('length2'),
                'success': True,
                'alignmentalphabet': 'ABCDEFGHIJKLMNOPQRSTUVXYZ'
        }

        sampleset2 = SampleSet(**sampleset2_data)
        sampleset2.save()

        response = self.client.get(reverse('victimID', kwargs={'victim_id': 1}))
        self.assertEqual(json.loads(response.content)['victim_details']['sourceip'], '192.168.1.5')
        self.assertEqual(json.loads(response.content)['target_details']['name'], 'ruptureit')
        self.assertEqual(json.loads(response.content)['attack_details'][0]['batch'], 0)
