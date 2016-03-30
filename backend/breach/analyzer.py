import operator
import collections
import logging

logger = logging.getLogger(__name__)


class AnalyzerError(Exception):
    pass


def decide_optimal_candidate(candidate_lengths, samples_per_sampleset):
    '''Take a dictionary of candidate alphabets and their associated
    accumulative lengths and decide which candidate alphabet is the best
    (minimum) with what confidence.

    Returns a pair with the decision. The first element of the pair is which
    candidate alphabet is best; the second element is the confidence level for
    the decision.
    '''

    assert(len(candidate_lengths) > 1)

    samplesets_per_candidate = len(candidate_lengths.items()[0][1])
    accumulated_candidate_lengths = []

    for candidate_alphabet, list_of_lengths in candidate_lengths.iteritems():
        accumulated_candidate_lengths.append({
            'candidate_alphabet': candidate_alphabet,
            'length': sum(list_of_lengths)
        })

    # Sort sampleset groups by length.
    sorted_candidate_lengths = sorted(
        accumulated_candidate_lengths,
        key=operator.itemgetter('length')
    )

    logger.debug('\n############################################################################')
    logger.debug('Candidate scoreboard:')
    for cand in sorted_candidate_lengths:
        logger.debug('\t{}: {}'.format(cand['candidate_alphabet'], cand['length']))

    # Extract candidate with minimum length and the next best competitor
    # candidate. In case of binary search, these will be the only two
    # candidates.
    min_candidate = sorted_candidate_lengths[0]
    next_best_candidate = sorted_candidate_lengths[1]

    samples_per_candidate = samplesets_per_candidate * samples_per_sampleset

    # Extract a confidence value, in bytes, for our decision based on the second-best candidate.
    confidence = float(next_best_candidate['length'] - min_candidate['length']) / samples_per_candidate

    # Captured bytes are represented as hex string,
    # so we need to convert confidence metric to bytes
    confidence /= 2.0

    return min_candidate['candidate_alphabet'], confidence


def decide_next_world_state(samplesets):
    '''Take a list of samplesets and extract a decision for a state transition
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
    '''
    # Ensure we have enough sample sets to compare.
    assert(len(samplesets) > 1)

    # Ensure all samplesets are extending the same known state
    knownsecret = samplesets[0].round.knownsecret
    round = samplesets[0].round
    amount = round.amount
    victim = round.victim
    target = victim.target
    for sampleset in samplesets:
        assert(sampleset.round == round)

    # Split samplesets based on alphabetvector under consideration
    # and collect data lengths for each candidate.
    candidate_lengths = collections.defaultdict(lambda: [])
    candidate_count_samplesets = collections.defaultdict(lambda: 0)
    for sampleset in samplesets:
        candidate_lengths[sampleset.candidatealphabet].append(len(sampleset.data))
        candidate_count_samplesets[sampleset.candidatealphabet] += 1

    candidate_count_samplesets = candidate_count_samplesets.items()

    samplesets_per_candidate = candidate_count_samplesets[0][1]

    for alphabet, count in candidate_count_samplesets:
        assert(count == samplesets_per_candidate)

    # Ensure we have a decision to make
    assert(len(candidate_lengths) > 1)

    min_vector, confidence = decide_optimal_candidate(candidate_lengths, samples_per_sampleset=amount)

    # use minimum group's alphabet vector
    decision_knownalphabet = min_vector
    # known secret remains the same as in all current samplesets
    decision_knownsecret = knownsecret

    if len(decision_knownalphabet) == 1:
        # decision vector was one character, so we can extend the known secret
        decision_knownsecret += decision_knownalphabet
        decision_knownalphabet = target.alphabet

    state = {
        'knownsecret': decision_knownsecret,
        'knownalphabet': decision_knownalphabet
    }

    return {
        'state': state,
        'confidence': confidence
    }
