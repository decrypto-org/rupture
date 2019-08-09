from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError
from breach.analyzer import decide_next_world_state
from breach.models import Target
from itertools import groupby


class Round(models.Model):
    class Meta:
        unique_together = (('victim', 'index'),)

    def get_method(self):
        return self.method

    def clean(self):
        if not self.knownsecret.startswith(self.victim.target.prefix):
            raise ValidationError('Knownsecret must start with known target prefix')

        if not set(self.knownalphabet) <= set(self.victim.target.alphabet):
            raise ValidationError("Knownalphabet must be a subset of target's alphabet")

    # Get the stored samplesets of the round.
    # For every round's batch, decide next world state based on all the
    # samplesets collected up to this batch and save the results in the attack_details_list.
    # Each element of the attack_details_list contains the needed details for each batch
    def fetch_per_batch_info(self):
        samplesets = self.sampleset_set.filter(round_id=self.id, success=True).order_by('batch')
        batch_info = []
        batches = groupby(samplesets, lambda x: x.batch)
        for batch, batch_samplesets in batches:
            list_batch_samplesets = list(batch_samplesets)
            decision = decide_next_world_state(list_batch_samplesets)
            batch_details = {
                'round': self.index,
                'knownsecret': self.knownsecret,
                'batch': batch,
                'alignmentalphabet': list_batch_samplesets[0].alignmentalphabet,
                'possible_knownprefix': decision['state']['knownsecret'],
                'confidence': decision['confidence']
            }
            batch_info.append(batch_details)
        return batch_info

    victim = models.ForeignKey('breach.Victim')

    index = models.IntegerField(
        default=1,
        help_text=('Which round of the attack this is. The first round has ',
                   'index 1.')
    )

    batch = models.IntegerField(
        default=0,
        help_text=('Which batch of the round is currently being attempted. '
                   'A new batch starts any time samplesets for the round '
                   'are created, either because the round is starting or '
                   'because not enough condidence was built.')
    )

    maxroundcardinality = models.IntegerField(
        default=1,
        help_text=('The maximum amount of symbols that will be tested in this '
                   'round by a single sampleset. '
                   'This can be larger or equal to the current sampleset\'s '
                   'candidatealphabet length, as other samplesets may not '
                   'have the same candidatealphabet length. This discrepancy '
                   'occurs when the target alphabet is not a perfect power of '
                   '2.')
    )

    minroundcardinality = models.IntegerField(
        default=1,
        help_text=('The minimum amount of symbols that will be tested in this '
                   'round by a single sampleset. '
                   'This can be less or equal to the current sampleset\'s '
                   'candidatealphabet length.')
    )

    amount = models.IntegerField(
        default=1,
        help_text='Number of samples contained in each sampleset of this round.'
    )

    # sampleset knownstate: knownsecret and knownalphabet
    knownsecret = models.CharField(
        default='',
        max_length=255,
        help_text='Known secret before the sample set was collected'
    )

    knownalphabet = models.CharField(
        max_length=255,
        help_text='The candidate alphabet for the next unknown character'
    )

    started = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text='Date and time since round was started'
    )

    completed = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text='When we stopped round, successfully or not'
    )

    accumulated_probability = models.FloatField(
        default=1.0,
        help_text='Accumulated probability of current round\'s given knownsecret. '
    )

    method = models.IntegerField(
        default=Target.SERIAL,
        choices=Target.METHOD_CHOICES,
        help_text='Method of building candidate samplesets.'
    )

    block_align = models.BooleanField(
        default=True,
        help_text=('Whether to use block alignment or not, in case '
                   'maxreflectionlength does not allow it')
    )

    huffman_pool = models.BooleanField(
        default=True,
        help_text=('Whether to use Huffman pool or not, in case '
                   'maxreflectionlength does not allow it')
    )

    huffman_balance = models.BooleanField(
        default=True,
        help_text=('Whether to use huffman balance for match symbols.')
    )
