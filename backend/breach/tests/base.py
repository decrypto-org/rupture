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

        # Different batch
        self.dif_batch_victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )
        dif_batch_round = Round.objects.create(
            victim=self.dif_batch_victim,
            amount=1,
            knownsecret='testsecret',
            knownalphabet='01',
        )
        self.dif_batch_samplesets = [
            SampleSet.objects.create(
                round=dif_batch_round,
                candidatealphabet='0',
                data='exlength'
            ),
            SampleSet.objects.create(
                round=dif_batch_round,
                candidatealphabet='1',
                data='length'
            )
        ]

        # Advance round
        self.next_round_victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.141',
            snifferendpoint='http://localhost/'
        )
        next_round_round = Round.objects.create(
            victim=self.next_round_victim,
            amount=1,
            knownsecret='testsecret',
            knownalphabet='01',
        )
        self.next_round_samplesets = [
            SampleSet.objects.create(
                round=next_round_round,
                candidatealphabet='0',
                data='bigbignextround'
            ),
            SampleSet.objects.create(
                round=next_round_round,
                candidatealphabet='1',
                data='smallround'
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

    def tearDown(self):
        for sampleset in self.balance_samplesets + self.samplesets + self.dif_batch_samplesets + self.next_round_samplesets:
            sampleset.completed = timezone.now()
            sampleset.save()
