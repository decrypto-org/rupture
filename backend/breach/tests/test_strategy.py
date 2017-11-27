from django.utils import timezone
from mock import patch
from binascii import hexlify

from breach.tests.base import RuptureTestCase
from breach.strategy import Strategy
from breach.models import Target, Victim, Round, SampleSet


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
        capture0 = {'data': 'exleng', 'records': 1}
        capture1 = {'data': 'length', 'records': 1}
        instance = Sniffer.return_value
        instance.read.return_value = capture0

        # Mock initial round
        mock_target = Target.objects.create(
            endpoint='https://di.uoa.gr/?breach=%s',
            prefix='test',
            alphabet='0123456789',
            name='webuoagr',
            confidence_threshold=1.0
        )

        dif_batch_victim = Victim.objects.create(
            target=mock_target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )
        dif_batch_round = Round.objects.create(
            victim=dif_batch_victim,
            amount=1,
            knownsecret='testsecret',
            knownalphabet='01',
        )
        self.dif_batch_samplesets = [
            SampleSet.objects.create(
                round=dif_batch_round,
                candidatealphabet='0',
                datalength=len(hexlify('length'))
            ),
            SampleSet.objects.create(
                round=dif_batch_round,
                candidatealphabet='1',
                datalength=len(hexlify('length'))
            )
        ]

        strategy0 = Strategy(dif_batch_victim)
        work0 = strategy0.get_work()
        strategy0.work_completed()

        instance.read.return_value = capture1
        strategy1 = Strategy(dif_batch_victim)
        work1 = strategy1.get_work()
        strategy1.work_completed()

        dif_batch_strategy0 = Strategy(dif_batch_victim)
        dif_batch_work0 = dif_batch_strategy0.get_work()

        dif_batch_strategy1 = Strategy(dif_batch_victim)
        dif_batch_work1 = dif_batch_strategy1.get_work()

        # Check if new Samplesets are equal to the original ones.
        self.assertEqual(dif_batch_work0, work0)
        self.assertEqual(dif_batch_work1, work1)

    @patch('breach.strategy.Sniffer')
    def test_create_multiple_branches(self, Sniffer):
        # Mock captured parameteres for Sniffer
        capture0 = {'data': 'small', 'records': 1}
        capture1 = {'data': 'small2', 'records': 1}
        capture2 = {'data': 'bigbigbigbigdata', 'records': 1}
        instance = Sniffer.return_value
        instance.read.return_value = capture0

        BACKTRACKING = 3

        # Mock initial round
        mock_target = Target.objects.create(
            endpoint='https://di.uoa.gr/?breach=%s',
            prefix='branch',
            alphabet='0123456789',
            name='github',
            secretlength=14,
            method=BACKTRACKING
        )

        change_branch_victim = Victim.objects.create(
            target=mock_target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )

        change_branch_round = Round.objects.create(
            victim=change_branch_victim,
            amount=1,
            knownsecret='branchsecret',
            knownalphabet='012',
        )

        change_branch_samplesets = [
            SampleSet.objects.create(
                round=change_branch_round,
                candidatealphabet='0',
                data='small'
            ),
            SampleSet.objects.create(
                round=change_branch_round,
                candidatealphabet='1', data='small2'
            ),
            SampleSet.objects.create(
                round=change_branch_round,
                candidatealphabet='2',
                data='bigbigbigbigdata'
            )
        ]

        strategy0 = Strategy(change_branch_victim)
        work0 = strategy0.get_work()
        self.assertTrue(work0)
        self.assertFalse(strategy0.work_completed())

        instance.read.return_value = capture1
        strategy1 = Strategy(change_branch_victim)
        work1 = strategy1.get_work()
        self.assertTrue(work1)
        self.assertFalse(strategy1.work_completed())

        instance.read.return_value = capture2
        strategy2 = Strategy(change_branch_victim)
        work2 = strategy2.get_work()
        self.assertTrue(work2)
        self.assertFalse(strategy2.work_completed())

        new_rounds = Round.objects.filter(
            victim=change_branch_victim,
            started=None
        )
        self.assertEqual(len(new_rounds), 3)

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
                datalength=len('bigbignextround')
            ),
            SampleSet.objects.create(
                round=next_round,
                candidatealphabet='1',
                datalength=len('smallround')
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

    @patch('breach.strategy.Sniffer')
    def test_divide_and_conquer(self, Sniffer):

        DIVIDE_CONQUER = 2
        # Mock initial round
        mock_target = Target.objects.create(
            endpoint='https://di.uoa.gr/?breach=%s',
            prefix='test',
            alphabet='0123',
            name='webuoa',
            method=DIVIDE_CONQUER
        )

        victim = self.create_mock_victim(mock_target)

        strategy0 = Strategy(victim)
        work0 = strategy0.get_work()
        self.assertEqual(
             work0['url'],
             'https://di.uoa.gr/?breach=^3^2^test1^test0^'
        )
        strategy0._mark_current_work_completed()

        strategy1 = Strategy(victim)
        work1 = strategy1.get_work()
        self.assertEqual(
            work1['url'],
            'https://di.uoa.gr/?breach=^1^0^test3^test2^'
        )
        strategy1._mark_current_work_completed()
