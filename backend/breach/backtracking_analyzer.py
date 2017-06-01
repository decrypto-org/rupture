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
    compression_function_factor = 1.3
    relative_probability_sum = 0.0
    min_candidate_value = sorted_candidate_lengths[0]['length']
    round_factor = 4
    amplification_factor = 1.2

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
