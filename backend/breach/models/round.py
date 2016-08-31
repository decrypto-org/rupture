from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError


class Round(models.Model):
    class Meta:
        unique_together = (('victim', 'index'),)

    def check_block_align(self):
        try:
            return self.block_align
        except AttributeError:
            self.block_align = self.victim.target.block_align
            return self.block_align

    def check_huffman_pool(self):
        try:
            return self.huffman_pool
        except AttributeError:
            self.huffman_pool = self.victim.target.huffman_pool
            return self.huffman_pool

    def get_method(self):
        try:
            return self.method
        except AttributeError:
            self.method = self.victim.target.method
            return self.method

    def clean(self):
        if not self.knownsecret.startswith(self.victim.target.prefix):
            raise ValidationError('Knownsecret must start with known target prefix')

        if not set(self.knownalphabet) <= set(self.victim.target.alphabet):
            raise ValidationError("Knownalphabet must be a subset of target's alphabet")

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
