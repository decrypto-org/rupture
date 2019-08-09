from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError


class SampleSet(models.Model):
    '''
    A set of samples collected for a particular victim pertaining to an
    alphabet vector used to extend a known secret.
    '''
    def clean(self):
        if self.round.maxroundcardinality < len(self.candidatealphabet):
            raise ValidationError('Sampleset alphabet should be at most maxroundcardinality sized.')
        if self.round.minroundcardinality > len(self.candidatealphabet):
            raise ValidationError('Sampleset alphabet should be at least minroundcardinality sized.')
        if set(self.candidatealphabet) > set(self.round.knownalphabet):
            raise ValidationError("Candidate alphabet must be a subset of round's known alphabet")
        if set(self.alignmentalphabet) != set(self.round.victim.target.alignmentalphabet):
            raise ValidationError("Alignment alphabet must be a permutation of target's alignmentalphabet")

    @staticmethod
    def create_sampleset(params):
        sampleset = SampleSet(**params)
        sampleset.save()
        try:
            sampleset.clean()
        except ValidationError, err:
            sampleset.delete()
            raise err
        return sampleset

    round = models.ForeignKey(
        'breach.Round',
        help_text=('Which round this sampleset belongs to. Each round '
                   'contains the collection of multiple samplesets pertaining '
                   'to different candidate alphabets. To complete a round, '
                   'enough samplesets must be completed to be able to make '
                   'a decision for a state transition with a certain '
                   'confidence.')
    )

    batch = models.IntegerField(
        default=0,
        help_text='The round batch that this sampleset belongs to.'
    )

    # candidate state
    candidatealphabet = models.CharField(
        max_length=255,
        help_text=('The alphabet vector that is attempted in this particular '
                   'sample set.'
                   'When performing a divide and conquer attack, this will '
                   'typically be a subset of the knownnextalphabet. In an '
                   'iterative attack, it will be a single symbol of '
                   'knownnextalphabet.')
    )

    alignmentalphabet = models.CharField(
        max_length=255,
        default='',
        help_text=('The alphabet used for padding in order to achieve block '
                   'alignment for this batch. This is a permutation of the '
                   'target alignment alphabet.')
    )

    datalength = models.IntegerField(
        default=0,
        help_text='The length of the raw data collected on the network for this sampleset'
    )

    records = models.IntegerField(
        default=0,
        help_text='The number of records that contain all the data.'
    )

    started = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text='Date and time at which sample set collection was started'
    )

    completed = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text=('When we stopped collecting samples for this sampleset, '
                   'successfully or not')
    )

    success = models.BooleanField(
        default=False,
        help_text=('Whether the samples in this sampleset were all collected '
                   'successfully')
    )

    huffman_match_balance = models.CharField(
        max_length=255,
        default='',
        help_text=('The alphabet used for balancing the Huffman tree for the '
                   'match pointers.')
    )
