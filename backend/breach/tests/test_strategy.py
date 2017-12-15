from mock import patch
from binascii import hexlify

from breach.tests.base import RuptureTestCase
from breach.strategy import Strategy
from breach.models import Target, Victim, Round, SampleSet


class StrategyTestCase(RuptureTestCase):
    @patch('breach.strategy.Sniffer')
    def test_knownsecret(self, Sniffer):
        strategy = Strategy(self.victim)
        self.assertEqual(
            strategy.get_decrypted_secret(),
            'testsecret'
        )

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
            huffman_balance=False
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
            name='ruptureit',
            huffman_balance=False
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
            huffman_balance=False
        )

        SampleSet.objects.create(
            round=next_round,
            candidatealphabet='0',
            datalength=len('bigbignextround')
        )
        SampleSet.objects.create(
            round=next_round,
            candidatealphabet='1',
            datalength=len('smallround')
        )

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
            method=DIVIDE_CONQUER,
            huffman_balance=False
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

    @patch('breach.strategy.Sniffer')
    def test_downgrade_huffman_balance(self, Sniffer):
        target = Target.objects.create(
            name='maxreflection',
            endpoint='https://test.com/?breach=%s',
            prefix='test',
            alphabet='0123',
            maxreflectionlength=30,
            method=2
        )

        victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )

        strategy = Strategy(victim)
        work = strategy.get_work()
        self.assertEqual(work, {'url': u'https://test.com/?breach=^3^2^test1^test0^', 'amount': 64, 'timeout': 0, 'alignmentalphabet': u''})

        target.delete()

    @patch('breach.strategy.Sniffer')
    def test_downgrade_to_serial(self, Sniffer):
        target = Target.objects.create(
            name='maxreflection',
            endpoint='https://test.com/?breach=%s',
            prefix='test',
            alphabet='0123',
            maxreflectionlength=16,
            method=2
        )

        victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )

        strategy = Strategy(victim)
        work = strategy.get_work()
        self.assertEqual(work, {'url': u'https://test.com/?breach=^1^3^2^test0^', 'amount': 64, 'timeout': 0, 'alignmentalphabet': u''})

        target.delete()

    @patch('breach.strategy.Sniffer')
    def test_downgrade_huffman(self, Sniffer):
        target = Target.objects.create(
            name='maxreflection',
            endpoint='https://test.com/?breach=%s',
            prefix='test',
            alphabet='0123',
            maxreflectionlength=12,
            method=2,
            huffman_balance=False
        )

        victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )

        strategy = Strategy(victim)
        work = strategy.get_work()
        self.assertEqual(work, {'url': u'https://test.com/?breach=^test0^', 'amount': 64, 'timeout': 0, 'alignmentalphabet': u''})

        target.delete()

    @patch('breach.strategy.Sniffer')
    def test_maxreflectionerror(self, Sniffer):
        target = Target.objects.create(
            name='maxreflection',
            endpoint='https://test.com/?breach=%s',
            prefix='test',
            alphabet='0123',
            maxreflectionlength=6,
            method=2,
            huffman_balance=False
        )

        victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )

        strategy = Strategy(victim)
        work = strategy.get_work()
        self.assertEqual(work, {})

        target.delete()
