import operator
import collections
import logging

logger = logging.getLogger(__name__)


def get_accumulated_probabilities(sorted_candidate_lengths, current_round_acc_probability):
    '''Take a dictionary of sorted candidate alphabets  and calculate the
    relative probability of each candidate being in the target secret based on
    their associated accumulative lengths. Then associate the relative values
    with the probability of the parent Round and calculate the final accumulated
    probability.

    Returns a dictionary containing every possible candidate alphabet and its
    accumulated probability value.
    '''
    compression_function_factor = 1.05
    relative_probability_sum = 0.0
    min_candidate_value = sorted_candidate_lengths[0]['length']
    round_factor = 4
    amplification_factor = 1.05

    # Calculate relative probability sum based on each candidate's length.
    for candidate in sorted_candidate_lengths:
        relative_probability_sum += (compression_function_factor **
                                     (-abs(candidate['length'] -
                                      min_candidate_value)))

        relative_probability_sum = round(relative_probability_sum, round_factor)

    accumulated_probabilities = []

    # Calculate every candidate's accumulated probability by multiplying its
    # parent's probability with the relative value of this round and an
    # amplification factor.

    for candidate in sorted_candidate_lengths:
        relative_prob = (round(float(compression_function_factor **
                                     (-abs(candidate['length'] -
                                      min_candidate_value))), round_factor) /
                         relative_probability_sum)

        accumulated_value = (amplification_factor *
                             current_round_acc_probability *
                             relative_prob)

        accumulated_probabilities.append({
            'candidate': candidate['candidate_alphabet'],
            'probability': accumulated_value
        })

    return accumulated_probabilities


def get_candidates(candidate_lengths, accumulated_prob):
    '''Take a dictionary of candidate alphabets and their associated
    accumulative lengths.

    Returns a list with each candidate and its accumulated probability.
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

    candidates_probabilities = get_accumulated_probabilities(sorted_candidate_lengths,
                                                             accumulated_prob)

    logger.debug('\n' + 75 * '#')
    logger.debug('Candidate scoreboard:')
    for cand in sorted_candidate_lengths:
        logger.debug('\t{}: {}'.format(cand['candidate_alphabet'], cand['length']))

    return candidates_probabilities


def decide_next_backtracking_world_state(samplesets, accumulated_prob):
    '''Take a list of samplesets and the accumulated probability of current
    round and extract a decision for a state transition with a certain
    probability for each candidate.

    Arguments:
    samplesets -- a list of samplesets.
    accumulated_prob -- the accumulated probability of current knownalpahbet.

    This list must must contain at least two elements so that we have some basis
    for comparison. Each of the list's elements must share the same world state
    (knownsecret and knownalphabet) so that we are comparing on the same basis.
    The samplesets must contain at least two different candidate alphabets so
    that a decision can be made. It can contain multiple samplesets collected
    over the same candidate alphabet.

    Returns an array of dictionary pairs. The first element of the pair is the new
    state of every candidate; the second element of the pair is the
    confidence with which the analyzer is suggesting the state transition.
    '''
    # Ensure we have enough sample sets to compare.
    assert(len(samplesets) > 1)

    # Ensure all samplesets are extending the same known state
    knownsecret = samplesets[0].round.knownsecret
    round = samplesets[0].round
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

    candidates = get_candidates(candidate_lengths, accumulated_prob)

    state = []
    # All candidates are returned in order to create new rounds.
    for i in candidates:
        state.append({
            'knownsecret': knownsecret + i['candidate'],
            'probability': i['probability'],
            'knownalphabet': target.alphabet
        })

    return state
