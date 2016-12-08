from django.test import Client, TestCase
from django.core.urlresolvers import reverse
from breach.models import Target
from breach.views import VictimListView
import json


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.target1 = Target.objects.create(
            name='ruptureit',
            endpoint='https://ruptureit.com/test.php?reflection=%s',
            prefix='imper',
            alphabet='abcdefghijklmnopqrstuvwxyz',
            secretlength=9,
            alignmentalphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            recordscardinality=1,
            method=1
        )

        self.target2 = Target.objects.create(
            name='ruptureit2',
            endpoint='https://ruptureit.com/test.php?reflection=%s',
            prefix='imper',
            alphabet='abcdefghijklmnopqrstuvwxyz',
            secretlength=9,
            alignmentalphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            recordscardinality=1,
            method=2
        )

        self.target1_data = {
            'name': 'ruptureit',
            'endpoint': 'https://ruptureit.com/test.php?reflection=%s',
            'prefix': 'imper',
            'alphabet': 'abcdefghijklmnopqrstuvwxyz',
            'secretlength': 9,
            'alignmentalphabet': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'recordscardinality': 1,
            'method': 1
        }

        self.target2_data = {
            'name': 'ruptureit2',
            'endpoint': 'https://ruptureit.com/test.php?reflection=%s',
            'prefix': 'imper',
            'alphabet': 'abcdefghijklmnopqrstuvwxyz',
            'secretlength': 9,
            'alignmentalphabet': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'recordscardinality': 1,
            'method': 2
        }

    def test_target_post(self):
        """
        Test post requests for /target
        """
        # Create the request
        data = {
            'name': 'ruptureit3',
            'endpoint': 'https://ruptureit.com/test.php?reflection=%s',
            'prefix': 'imper',
            'alphabet': 'abcdefghijklmnopqrstuvwxyz',
            'secretlength': 9,
            'alignmentalphabet': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'recordscardinality': 1,
            'method': 1
        }
        response = self.client.post(reverse('TargetView'), json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['target_name'], 'ruptureit3')

    def test_target_get(self):

        response = self.client.get(reverse('TargetView'))
        response_dict1 = {key: json.loads(response.content)['targets'][0][key] for key in self.target1_data}
        response_dict2 = {key: json.loads(response.content)['targets'][1][key] for key in self.target2_data}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_dict1, self.target1_data)
        self.assertEqual(response_dict2, self.target2_data)
