from django.test import TestCase
from breach.models import SampleSet, Victim, Target, Round


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

        # Balance checking
        self.balance_victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )
        balance_round = Round.objects.create(
            victim=self.balance_victim,
            amount=1,
            knownsecret='testsecret',
            knownalphabet='0123',
            roundcardinality=3
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
