from __future__ import unicode_literals
from django.db import models


class Victim(models.Model):
    '''
    A particular instance of a target for a particular user-victim
    e.g. dionyziz@gmail.com
    '''

    target = models.ForeignKey('breach.Target')

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

    calibration_wait = models.FloatField(
        default=0.0,
        help_text=('The amount of time in seconds that sniffer should wait '
                   'so that Scapy has enough time to lock on low-level network '
                   'resources.')
    )

    recordscardinality = models.IntegerField(
        default=0,
        help_text=('The amount of expected TLS response records per request. '
                   'If 0 then the amount is not known or is expected to '
                   'change per request.')
    )
