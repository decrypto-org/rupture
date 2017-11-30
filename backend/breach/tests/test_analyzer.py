from breach.tests.base import RuptureTestCase
from breach.analyzer import decide_next_world_state
from breach.backtracking_analyzer import decide_next_backtracking_world_state


class AnalyzerTestCase(RuptureTestCase):
    def test_decide(self):
        decision = decide_next_world_state(self.samplesets)

        state = decision['state']

        self.assertEqual(state['knownsecret'], 'testsecret1')
        self.assertEqual(state['knownalphabet'], '0123456789')

    def test_decide_backtracking(self):
        # decide_next_backtracking_world requires the accumulated probability of
        # current round as second argument. The default value for each round
        # model is 1.0.
        decision = decide_next_backtracking_world_state(self.samplesets, 1.0)

        self.assertEqual(decision[0]['knownsecret'], 'testsecret1')
        self.assertEqual(decision[0]['knownalphabet'], '0123456789')
        self.assertEqual(decision[1]['knownsecret'], 'testsecret0')
        self.assertEqual(decision[1]['knownalphabet'], '0123456789')
