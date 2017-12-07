from mock import patch

from breach.tests.base import RuptureTestCase
from breach.strategy import Strategy
from breach.models import Target, Victim, Round, SampleSet
from breach.backtracking_analyzer import decide_next_backtracking_world_state


class BacktrackingTestCase(RuptureTestCase):
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

        SampleSet.objects.create(
            round=change_branch_round,
            candidatealphabet='0',
            datalength=len('small')
        )
        SampleSet.objects.create(
            round=change_branch_round,
            candidatealphabet='1',
            datalength=len('small2')
        )
        SampleSet.objects.create(
            round=change_branch_round,
            candidatealphabet='2',
            datalength=len('bigbigbigbigdata')
        )

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

    def test_decide_backtracking(self):
        # decide_next_backtracking_world requires the accumulated probability of
        # current round as second argument. The default value for each round
        # model is 1.0.
        decision = decide_next_backtracking_world_state(self.samplesets, 1.0)

        self.assertEqual(decision[0]['knownsecret'], 'testsecret1')
        self.assertEqual(decision[0]['knownalphabet'], '0123456789')
        self.assertEqual(decision[1]['knownsecret'], 'testsecret0')
        self.assertEqual(decision[1]['knownalphabet'], '0123456789')
