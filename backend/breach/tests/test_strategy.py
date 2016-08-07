from django.utils import timezone
from mock import patch

from breach.tests.base import RuptureTestCase
from breach.strategy import Strategy
from breach.models import SampleSet
from breach.models import Round
from breach.models import Target
from breach.models import Victim


class StrategyTestCase(RuptureTestCase):
    @patch('breach.strategy.Sniffer')
    def test_first_round(self, Sniffer):
        strategy0 = Strategy(self.victim)

        work0 = strategy0.get_work()
        self.assertEqual(
            work0['url'],
            'https://di.uoa.gr/?breach=^1^testsecret0^'
        )
        self.assertTrue('amount' in work0)
        self.assertTrue('timeout' in work0)

        strategy0._mark_current_work_completed()

        strategy1 = Strategy(self.victim)

        work1 = strategy1.get_work()
        self.assertEqual(
            work1['url'],
            'https://di.uoa.gr/?breach=^0^testsecret1^'
        )

        strategy1._mark_current_work_completed()

    def test_same_round_same_batch(self):
        pass

    def test_same_round_different_batch(self):
        pass

    @patch('breach.strategy.Sniffer')
    def test_advance_round(self, Sniffer):
        # Mock captured parameteres for Sniffer
        capture0 = {'data': 'bigbignextround', 'records': 1}
        capture1 = {'data': 'smallround', 'records': 1}
        instance = Sniffer.return_value
        instance.read.return_value = capture0

        # Mock initial round
        mock_target = Target.objects.create(
            endpoint='https://di.uoa.gr/?breach=%s',
            prefix='test',
            alphabet='0123456789',
            name='ruptureit'
        )

        next_round_victim = Victim.objects.create(
            target=mock_target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )

        next_round = Round.objects.create(
            victim=next_round_victim,
            amount=1,
            knownsecret='testsecret',
            knownalphabet='01',
        )

        next_round_samplesets = [
            SampleSet.objects.create(
                round=next_round,
                candidatealphabet='0',
                data='bigbignextround'
            ),
            SampleSet.objects.create(
                round=next_round,
                candidatealphabet='1',
                data='smallround'
            )
        ]

        strategy0 = Strategy(next_round_victim)
        work0 = strategy0.get_work()
        self.assertTrue(work0)
        self.assertFalse(strategy0.work_completed())

        instance.read.return_value = capture1
        strategy1 = Strategy(next_round_victim)
        work1 = strategy1.get_work()
        self.assertTrue(work1)
        self.assertFalse(strategy1.work_completed())

        new_round_strategy = Strategy(next_round_victim)
        new_round_work = new_round_strategy.get_work()
        self.assertEqual(
            new_round_work['url'],
            'https://di.uoa.gr/?breach=^1^3^2^5^4^7^6^9^8^testsecret10^'
        )

    @patch('breach.strategy.Sniffer')
    def test_alphabet_balance(self, Sniffer):
        strategy0 = Strategy(self.balance_victim)
        work0 = strategy0.get_work()
        self.assertEqual(
            work0['url'],
            # testsecret5 and testsecret4 are dummy balancing secrets
            'https://di.uoa.gr/?breach=^1^3^2^testsecret0^testsecret5^testsecret4^'
        )

        strategy0._mark_current_work_completed()

        strategy1 = Strategy(self.balance_victim)
        work1 = strategy1.get_work()
        self.assertEqual(
            work1['url'],
            'https://di.uoa.gr/?breach=^0^5^4^testsecret3^testsecret2^testsecret1^'
        )

        strategy1._mark_current_work_completed()
