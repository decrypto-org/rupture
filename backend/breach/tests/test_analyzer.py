from breach.tests.base import RuptureTestCase
from breach.analyzer import decide_next_world_state


class AnalyzerTestCase(RuptureTestCase):
    def test_decide(self):
        decision = decide_next_world_state(self.samplesets)

        state = decision['state']
        confidence = decision['confidence']

        self.assertEqual(state[0]['knownsecret'], 'testsecret1')
        self.assertEqual(state[0]['knownalphabet'], '0123456789')
