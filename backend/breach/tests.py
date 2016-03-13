from django.test import TestCase
from breach.models import SampleSet, Victim, Target, Round
from breach.analyzer import decide_next_world_state


class RuptureTestCase(TestCase):
    def setUp(self):
        target = Target.objects.create(
            endpoint='http://di.uoa.gr/',
            prefix='test',
            alphabet='0123456789'
        )
        victim = Victim.objects.create(
            target=target,
            sourceip='192.168.10.140',
            snifferendpoint='http://localhost/'
        )
        round = Round.objects.create(
            victim=victim,
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

class AnalyzerTestCase(RuptureTestCase):
    def test_decide(self):
        state, confidence = decide_next_world_state(self.samplesets)

        self.assertEqual(state["knownsecret"], "testsecret1")
