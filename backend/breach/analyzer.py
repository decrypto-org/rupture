import operator
import collections
from itertools import groupby


class AnalyzerError(Exception):
    pass


def decide_optimal_candidate(candidates):
    """Take a dictionary of candidate alphabets and their associated
    accumulative lengths and decide which candidate alphabet is the best
    (minimum) with what confidence.

    Returns a pair with the decision. The first element of the pair is which
    candidate alphabet is best; the second element is the confidence level for
    the decision.
    """

    # sort sampleset groups by length
    sorted_candidate_lengths = sorted(
        candidates.items(),
        key=operator.itemgetter(1)
    )

    # Extract candidate with minimum length and the next best competitor
    # candidate. In case of binary search, these will be the only two
    # candidates.
    min_candidate = sorted_candidate_lengths[0]
    next_best_candidate = sorted_candidate_lengths[1]

    min_candidate_length = min_candidate[1]
    min_candidate_alphabet = min_candidate[0]

    next_best_length = next_best_candidate[1]

    # extract a confidence value for our decision based on the second-best candidate
    confidence = float(next_best_length - min_candidate_length) / next_best_length

    return min_candidate_alphabet, confidence


def decide_next_world_state(samplesets):
    """Take a list of samplesets and extract a decision for a state transition
    with some confidence.

    Argument:
    samplesets -- a list of samplesets.

    This list must must contain at least two elements so that we have some basis
    for comparison. Each of the list's elements must share the same world state
    (knownsecret and knownalphabet) so that we are comparing on the same basis.
    The samplesets must contain at least two different candidate alphabets so
    that a decision can be made. It can contain multiple samplesets collected
    over the same candidate alphabet.

    Returns a pair with the decision. The first element of the pair is the new
    state of the world; the second element of the pair is the confidence with
    which the analyzer is suggesting the state transition.
    """
    # Ensure we have enough sample sets to compare.
    assert(len(samplesets) > 1)

    # Ensure all samplesets are extending the same known state
    knownsecret = samplesets[0].knownsecret
    knownalphabet = samplesets[0].knownalphabet
    amount = samplesets[0].amount
    victim = samplesets[0].victim
    target = victim.target
    for sampleset in samplesets:
        assert(sampleset.knownsecret == knownsecret)
        assert(sampleset.knownalphabet == knownalphabet)
        assert(sampleset.victim == victim)
        assert(sampleset.amount == amount)

    # Split samplesets based on alphabetvector under consideration
    # and accumulate data lengths for each candidate.
    candidate_lengths = collections.defaultdict(lambda: 0)
    candidate_count_samplesets = collections.defaultdict(lambda: 0)
    for sampleset in samplesets:
        candidate_lengths[sampleset.candidatealphabet] += len(sampleset.data)
        candidate_count_samplesets[sampleset.candidatealphabet] += 1

    candidate_count_samplesets = candidate_count_samplesets.items()

    samplesets_per_candidate = candidate_count_samplesets[0][1]

    for alphabet, count in candidate_count_samplesets:
        assert(count == samplesets_per_candidate)

    # Ensure we have a decision to make
    assert(len(candidate_lengths) > 1)

    min_vector, confidence = decide_optimal_candidate(candidate_lengths)

    # use minimum group's alphabet vector
    decision_knownalphabet = min_vector
    # known secret remains the same as in all current samplesets
    decision_knownsecret = knownsecret

    if len(decision_knownalphabet) == 1:
        # decision vector was one character, so we can extend the known secret
        decision_knownsecret += decision_knownalphabet
        decision_knownalphabet = target.alphabet

    state = {
        "knownsecret": decision_knownsecret,
        "knownalphabet": decision_knownalphabet
    }

    return state, confidence
