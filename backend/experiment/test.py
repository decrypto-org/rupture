from django.test import TestCase
from breach.models import Target, Victim
from wrapped_tls import MockSniffer, get_response
from breach.strategy import Strategy
from mock import patch

import logging
logger = logging.getLogger(__name__)


class UnitTestCase(TestCase):
    @patch('breach.strategy.Sniffer', side_effect=MockSniffer)
    def test_div_conq_different_all_alphabets(self, mock_sniffer):
        target = Target.objects.create(
            endpoint='https://ruptureit.com/test2.php?reflection=%s',
            prefix='biben',
            alphabet='abcdefghijklmnopqrstuvwxyz',
            alignmentalphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            secretlength=8,
            recordscardinality=1,
            samplesize=1,
            name='ruptureit',
            method=2,  # 1: serial, 2: div&conq
            confidence_threshold=0.1
        )

        victim = Victim.objects.create(
            target=target,
            sourceip='0.0.0.0',
            snifferendpoint='http://localhost/'
        )

        while True:
            strategy = Strategy(victim)
            sniffer = strategy.sniffer

            work = strategy.get_work()
            url = work['url']
            samplesize = work['amount']
            sniffer.set_samplesize(samplesize)
            alignmentalphabet = work['alignmentalphabet'][:16]

            requests = [str(url + alignmentalphabet[sample_id % 16] + '^') for sample_id in range(samplesize)]
            app_data = ''.join([get_response(req) for req in requests])

            sniffer.set_data(app_data)
            completed = strategy.work_completed()
            if completed:
                break

        strategy = Strategy(victim)
        assert(strategy.get_decrypted_secret() == 'bibendum')
