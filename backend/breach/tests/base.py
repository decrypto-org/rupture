from django.utils import timezone
from django.test import TestCase
from breach.models import SampleSet, Victim, Target, Round


class RuptureTestCase(TestCase):
    def setUp(self):
        target = Target.objects.create(
            endpoint='https://di.uoa.gr/?breach=%s',
            prefix='test',
            alphabet='0123456789'
        )

        self.victim = self.create_mock_victim(target)

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

        # Balance checking
        self.balance_victim = self.create_mock_victim(target)

        balance_round = Round.objects.create(
            victim=self.balance_victim,
            amount=1,
            knownsecret='testsecret',
            knownalphabet='0123',
            minroundcardinality=1,
            maxroundcardinality=3
        )
        self.balance_samplesets = [
            SampleSet.objects.create(
                round=balance_round,
                candidatealphabet='0',
                data='bigbigbigbigbigbig'
            ),
            SampleSet.objects.create(
                round=balance_round,
                candidatealphabet='123',
                data='small'
            )
        ]

    def create_mock_victim(self, target):

        mock_victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.140',
            snifferendpoint='http://localhost/'
        )
        return mock_victim

    def tearDown(self):
        for sampleset in self.balance_samplesets + self.samplesets:
            sampleset.completed = timezone.now()
            sampleset.save()
