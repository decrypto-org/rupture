import operator
import collections
import logging

logger = logging.getLogger(__name__)


class AnalyzerError(Exception):
    pass


def get_accumulated_probabilities(sorted_candidate_lengths, current_round_acc_probability):
    '''Take a dictionary of sorted candidate alphabets  and calculate the
    relative probability of each candidate being in the target secret based on
    their associated accumulative lengths. Then associate the relative values
    with the probability of the parent Round and calculate the final accumulated
    probability.

    Returns a dictionary containing every possible candidate alphabet and its
    accumulated probability value.
    '''
    compression_function_factor = 1.3
    relative_probability_sum = 0.0
    min_candidate_value = sorted_candidate_lengths[0]['length']
    round_factor = 4
    amplification_factor = 1.2

    # Calculate relative probability sum based on each candidate's length.
    for length in sorted_candidate_lengths.values():
        relative_probability_sum += (compression_function_factor ** (-abs(length
                                                                          - min_candidate_value)))

        relative_probability_sum = round(relative_probability_sum, round_factor)

    accumulated_probabilities = []

    # Calculate every candidate's accumulated probability by multiplying its
    # parent's probability with the relative value of this round and an amplification
    # factor.
    for candidate, length in sorted_candidate_lengths.iteritems():
        relative_prob = (round(float(compression_function_factor
                                     ** (-abs(length - min_candidate_value))), round_factor)
                                     / relative_probability_sum)

        accumulated_value = amplification_factor * current_round_acc_probability * relative_prob
        accumulated_probabilities.append({
            'candidate_alphabet': candidate,
            'accumulated_probability': accumulated_value
        })

    return accumulated_probabilities

def decide_optimal_candidates(candidate_lengths, samples_per_sampleset):
    '''Take a dictionary of candidate alphabets and their associated
    accumulative lengths and decide which candidate alphabets are the best
    (below average value) with what confidence(worst optimal candidate's
    distance from average value).

    Returns a pair with the decision. The first element of the pair is which
    candidate alphabets are best; the second element is the confidence level for
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

    optimal_candidates = []
    average_threshold = sum(item['length'] for item in sorted_candidate_lengths) / len(sorted_candidate_lengths)

    # Candidates with accumulated length below average value have a possible
    # secret match, so they are returned.
    logger.debug('\n' + 75 * '#')
    logger.debug('Candidate scoreboard:')
    for cand in sorted_candidate_lengths:
        logger.debug('\t{}: {}'.format(cand['candidate_alphabet'], cand['length']))
        if(cand['length'] < average_threshold):
            optimal_candidates.append({
                'candidate': cand['candidate_alphabet'],
                'length': cand['length']
            })

    samples_per_candidate = samplesets_per_candidate * samples_per_sampleset

    # Extract a confidence value, in bytes, for our decision based on the worst optimal candidate's
    # distance from average value.
    confidence = float(average_threshold - optimal_candidates[-1]['length']) / samples_per_candidate

    # Captured bytes are represented as hex string,
    # so we need to convert confidence metric to bytes
    confidence /= 2.0

    return optimal_candidates, confidence


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
    state of every optimal candidate; the second element of the pair is the
    confidence with which the analyzer is suggesting the state transition.
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

    optimal_candidates, confidence = decide_optimal_candidates(candidate_lengths, samples_per_sampleset=amount)

    state = []
    # All optimal candidates are returned in order to create new rounds.
    for i in optimal_candidates:
        state.append({
            'knownsecret': knownsecret + i['candidate'],
            'knownalphabet': target.alphabet
        })

    return {
        'state': state,
        'confidence': confidence
    }
