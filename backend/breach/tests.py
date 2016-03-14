from django.test import TestCase
from mock import patch
from breach.models import SampleSet, Victim, Target, Round
from breach.strategy import Strategy
from breach.analyzer import decide_next_world_state


@patch('sniffer.Sniffer')
class RuptureTestCase(TestCase):
    def setUp(self):
        target = Target.objects.create(
            endpoint='https://di.uoa.gr/?breach=%s',
            prefix='test',
            alphabet='0123456789'
        )
        self.victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.140',
            snifferendpoint='http://localhost/'
        )
        round = Round.objects.create(
            victim=self.victim,
            amount=1,
            knownsecret='testsecret',
            knownalphabet='01'
        )
        self.samplesets = [
            SampleSet.objects.create(
                round=round,
                candidatealphabet='0',
                data='bigbigbigbigbigbig'
            ),
            SampleSet.objects.create(
                round=round,
                candidatealphabet='1',
                data='small'
            )
        ]


class StrategyTestCase(RuptureTestCase):
    @patch('breach.strategy.Sniffer')
    def test_first_round(self, Sniffer):
        strategy0 = Strategy(self.victim)

        work0 = strategy0.get_work()
        self.assertEqual(
            work0['url'],
            'https://di.uoa.gr/?breach=^testsecret0^1^3^2^5^4^7^6^9^8^'
        )
        self.assertTrue('amount' in work0)
        self.assertTrue('timeout' in work0)

        strategy1 = Strategy(self.victim)

        work1 = strategy1.get_work()
        self.assertEqual(
            work1['url'],
            'https://di.uoa.gr/?breach=^testsecret1^0^3^2^5^4^7^6^9^8^'
        )

    def test_same_round_same_batch(self):
        pass

    def test_same_round_different_batch(self):
        pass

    def test_advance_round(self):
        pass


class AnalyzerTestCase(RuptureTestCase):
    def test_decide(self):
        decision = decide_next_world_state(self.samplesets)

        state = decision['state']
        confidence = decision['confidence']

        self.assertEqual(state['knownsecret'], 'testsecret1')
        self.assertEqual(state['knownalphabet'], '0123456789')
