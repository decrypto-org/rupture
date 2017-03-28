from __future__ import unicode_literals
from django.db import models
import urlparse

from django.core.validators import RegexValidator


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

    alphanumeric = RegexValidator(r'^(?:([A-Za-z0-9])(?!.*\1))*$', 'Only alphanumeric characters are allowed.')

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
        validators=[alphanumeric],
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
        validators=[alphanumeric],
        help_text=('Alphabet used for block alignment. This will be shuffled '
                   'once per batch.')
    )

    recordscardinality = models.IntegerField(
        default=0,
        help_text=('The amount of expected TLS response records per request. '
                   'If 0 then the amount is not known or is expected to '
                   'change per request.')
    )

    sentinel = models.CharField(
        max_length=1,
        default='^',
        help_text=('Character used to seperate the complementary huffman '
                   'characters, in order to avoid unwanted compression.')
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

    confidence_threshold = models.FloatField(
        default=1.0,
        help_text=('The threshold that is used for confidence, in order '
                   'to determine whether a candidate should be chosen.')
    )
