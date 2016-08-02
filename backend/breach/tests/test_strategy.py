from django.utils import timezone
from mock import patch

from breach.tests.base import RuptureTestCase
from breach.strategy import Strategy
from breach.models import SampleSet


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

    @patch('breach.strategy.Sniffer')
    def test_same_round_different_batch(self, Sniffer):
        
        # Mock captured parameteres for Sniffer
        capture0 = {'data': 'exlength', 'records': 1}
        capture1 = {'data': 'length', 'records': 1}
        instance = Sniffer.return_value
        instance.read.return_value = capture0

        strategy0 = Strategy(self.dif_batch_victim)
        work0 = strategy0.get_work()
        self.assertTrue(work0)
        self.assertFalse(strategy0.work_completed())


        instance.read.return_value = capture1
        strategy1 = Strategy(self.dif_batch_victim)
        work1 = strategy1.get_work()
        self.assertTrue(work1)
        self.assertFalse(strategy1.work_completed())

        samplesets_to_check = SampleSet.objects.filter(
            round=strategy1._round
        )
        
        # Test if the sampleset's new batch is the same with the old one
        self.assertEqual(samplesets_to_check[0].round, samplesets_to_check[2].round)  
        self.assertEqual(samplesets_to_check[0].candidatealphabet, samplesets_to_check[2].candidatealphabet)  
        self.assertEqual(samplesets_to_check[0].alignmentalphabet, samplesets_to_check[2].alignmentalphabet)  
        self.assertNotEqual(samplesets_to_check[0].batch, samplesets_to_check[2].batch)  

    @patch('breach.strategy.Sniffer')
    def test_advance_round(self, Sniffer):
        # Mock captured parameteres for Sniffer
        capture0 = {'data': 'bigbignextround', 'records': 1}
        capture1 = {'data': 'smallround', 'records': 1}
        instance = Sniffer.return_value
        instance.read.return_value = capture0

        strategy0 = Strategy(self.next_round_victim)
        work0 = strategy0.get_work()
        self.assertTrue(work0)
        self.assertFalse(strategy0.work_completed())


        instance.read.return_value = capture1
        strategy1 = Strategy(self.next_round_victim)
        work1 = strategy1.get_work()
        self.assertTrue(work1)
        self.assertFalse(strategy1.work_completed())

        # Check if new samplesets have been created for the next round
        next_round_samplesets = list()
        samplesets_to_check = SampleSet.objects.filter()

        for sample in samplesets_to_check:
            if (sample.round.index==2):           
                next_round_samplesets.append(sample)
    
        alphabet = '0123456789'
        index = 0

        for sampleset in next_round_samplesets:
            self.assertEqual(sampleset.round.knownsecret, 'testsecret1')
            self.assertEqual(sampleset.candidatealphabet, alphabet[index])
            index +=1

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
