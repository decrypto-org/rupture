from mock import patch

from breach.tests.base import RuptureTestCase
from breach.strategy import Strategy


class StrategyTestCase(RuptureTestCase):
    @patch('breach.strategy.Sniffer')
    def test_first_round(self, Sniffer):
        strategy0 = Strategy(self.victim)

        work0 = strategy0.get_work()
        self.assertEqual(
            work0['url'],
            'https://di.uoa.gr/?breach=^testsecret0^1^'
        )
        self.assertTrue('amount' in work0)
        self.assertTrue('timeout' in work0)

        strategy1 = Strategy(self.victim)

        work1 = strategy1.get_work()
        self.assertEqual(
            work1['url'],
            'https://di.uoa.gr/?breach=^testsecret1^0^'
        )

    def test_same_round_same_batch(self):
        pass

    def test_same_round_different_batch(self):
        pass

    def test_advance_round(self):
        pass
