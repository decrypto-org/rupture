from __future__ import unicode_literals
from django.db import models
from django.core.exceptions import ValidationError
import urlparse


class Target(models.Model):
    '''
    A particular static target endpoint that the attack can apply to
    e.g. gmail csrf, facebook message
    '''

    endpoint = models.CharField(
        max_length=255,
        help_text=('The endpoint in full URL form, including \'https://\'.'
                   'The endpoint string must contain a \'%s\' to mark the '
                   'position in which the string-to-be-reflected will be '
                   'replaced into.')
    )

    @property
    def host(self):
        return urlparse.urlparse(self.endpoint).hostname

    name = models.CharField(
        default='',
        unique=True,
        max_length=255,
        help_text=('A unique name identifying the target.')
    )

    port = models.IntegerField(
        default=443,
        help_text=('The port that responses are expected to come from. '
                   'For TLS this should generally be 443.')
    )

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

    alignmentalphabet = models.CharField(
        max_length=255,
        default='',
        help_text=('Alphabet used for block alignment. This will be shuffled '
                   'once per batch.')
    )

    recordscardinality = models.IntegerField(
        default=0,
        help_text=('The amount of expected TLS response records per request. '
                   'If 0 then the amount is not known or is expected to '
                   'change per request.')
    )

    SERIAL = 1
    DIVIDE_CONQUER = 2
    METHOD_CHOICES = (
        (SERIAL, 'serial'),
        (DIVIDE_CONQUER, 'divide&conquer'),
    )

    method = models.IntegerField(
        default=SERIAL,
        choices=METHOD_CHOICES,
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

    samplesize = models.IntegerField(
        default=64,
        help_text=('The amount of samples per sampleset.')
    )


class Victim(models.Model):
    '''
    A particular instance of a target for a particular user-victim
    e.g. dionyziz@gmail.com
    '''
    target = models.ForeignKey(Target)

    snifferendpoint = models.CharField(
        max_length=255,
        help_text=("The HTTP endpoint of the adversarial sniffer running on "
                   "the victim's network which is listening for our HTTP "
                   "requests. This endpoint must include the 'http://' "
                   "prefix.")
    )

    sourceip = models.GenericIPAddressField(
        help_text='Source IP on the local network, e.g. 192.168.10.140'
    )

    interface = models.CharField(
        default='wlan0',
        max_length=255,
        help_text=("Attacking machine's interface that is on the victim's "
                   "network.")
    )

    realtimeurl = models.CharField(
        default='http://localhost:3031',
        max_length=255,
        help_text=("The realtime module URL that the client should "
                   "communicate with. This URL must include the "
                   "'http://' prefix.")
    )


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

    victim = models.ForeignKey(Victim)

    index = models.IntegerField(
        default=1,
        help_text=('Which round of the attack this is. The first round has ',
                   'index 1.')
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

    data = models.TextField(
        default='',
        help_text='The raw data collected on the network for this sampleset'
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
