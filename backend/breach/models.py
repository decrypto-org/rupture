from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

import urlparse


class Target(models.Model):
    '''
    A particular static target endpoint that the attack can apply to
    e.g. gmail csrf, facebook message
    '''

    endpoint = models.CharField(
        max_length=255,
        help_text=('The endpoint in full URL form, including 'https://'.'
                   'The endpoint string must contain a '%s' to mark the '
                   'position in which the string-to-be-reflected will be '
                   'replaced into.')
    )

    @property
    def host(self):
        return urlparse.urlparse(self.endpoint).hostname

    maxreflectionlength = models.IntegerField(
        default=0,
        help_text=('The maximum length that will be reflected by the service '
                   'the designated location within the endpoint. If this is 0 '
                   'then there is no limit in the reflection length.')
    )

    prefix = models.CharField(
        max_length=255,
        help_text=('The known prefix of the secret used to bootstrap the '
                   'attack.')
    )

    alphabet = models.CharField(
        max_length=255,
        help_text=('This set contains all the candidate symbols each ',
                   'character of the secret can be.')
    )

    secretlength = models.IntegerField(
        default=0,
        help_text=('The length of the secret, if known. If the length of the '
                   'secret is unknown, leave this as 0.')
    )


class Victim(models.Model):
    '''
    A particular instance of a target for a particular user-victim
    e.g. dionyziz@gmail.com
    '''
    target = models.ForeignKey(Target)
    snifferendpoint = models.CharField(
        max_length=255,
        help_text=('The HTTP endpoint of the adversarial sniffer running on '
                   'the victim\'s network which is listening for our HTTP '
                   'requests. This endpoint must include the \'http://\' '
                   'prefix.')
    )
    sourceip = models.GenericIPAddressField(
        help_text='Source IP on the local network, e.g. 192.168.10.140'
    )
    # TODO: method (divide & conquer, etc.)


class Round(models.Model):
    class Meta:
        unique_together = (('victim', 'index'),)

    victim = models.ForeignKey(Victim)
    index = models.IntegerField(
        default=1,
        help_text=('Which round of the attack this is. The first round has ',
                   'index 1.')
    )
    roundcardinality = models.IntegerField(
        default=1,
        help_text=('How many alphabet symbols are being tested in this round.'
                   'This can be larger or equal to the current sampleset\'s '
                   'candidatealphabet length, as other samplesets may not '
                   'have the same candidatealphabet length. This discrepancy '
                   'occurs when the target alphabet is not a perfect power of '
                   '2.')
    )
    # assert(self.roundcardinality >= len(self.candidatealphabet))

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
    # assert(
    #     self.knownsecret[0:len(self.victim.target.prefix)]
    #     ==
    #     self.victim.target.prefix
    # )
    knownalphabet = models.CharField(
        max_length=255,
        help_text='The candidate alphabet for the next unknown character'
    )
    # assert(
    #     all([c in self.victim.target.alphabet for c in self.knownalphabet])
    # )


class SampleSet(models.Model):
    '''
    A set of samples collected for a particular victim pertaining to an
    alphabet vector used to extend a known secret.
    '''

    round = models.ForeignKey(
        Round,
        help_text=('Which round this sampleset belongs to. Each round '
                   'contains the collection of multiple samplesets pertaining '
                   'to different candidate alphabets. To complete a round, '
                   'enough samplesets must be completed to be able to make '
                   'a decision for a state transition with a certain '
                   'confidence.')
    )
    # assert(self.round.index <= self.victim.round.index)

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
    # assert(all([c in self.knownalphabet for c in self.candidatealphabet]))

    data = models.TextField(
        default='',
        help_text='The raw data collected on the network for this sampleset'
    )

    started = models.DateTimeField(
        default=timezone.now,
        help_text='Date and time at which sample set collection was started'
    )
    completed = models.DateTimeField(
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
