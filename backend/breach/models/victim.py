from __future__ import unicode_literals
from django.db import models
from breach.helpers import injector
from django.utils import timezone


class Victim(models.Model):
    '''
    A particular instance of a target for a particular user-victim
    e.g. dionyziz@gmail.com
    '''
    def attack(self):
        injector.inject(self)

    @property
    def percentage(self):
        rounds = self.round_set.all()
        round_details = sorted(list(rounds.values('knownsecret')))
        try:
            return "{:.2f}".format((len(round_details[len(round_details) - 1]['knownsecret']) / self.target.secretlength) * 100)
        except:
            return '0'

    @property
    def running_time(self):
        return (timezone.now() - self.attacked_at).total_seconds()

    def delete(self):
        self.trashed_at = timezone.now()
        self.save()

    def restore(self):
        self.trashed_at = None
        self.save()

    target = models.ForeignKey('breach.Target', null=True, blank=True)

    snifferendpoint = models.CharField(
        default='http://127.0.0.1:9000',
        max_length=255,
        help_text=("The HTTP endpoint of the adversarial sniffer running on "
                   "the victim's network which is listening for our HTTP "
                   "requests. This endpoint must include the 'http://' "
                   "prefix.")
    )

    sourceip = models.GenericIPAddressField(
        help_text='Source IP on the local network, e.g. 192.168.10.140'
    )

    trashed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=('The datatime of the delete request.')
    )

    interface = models.CharField(
        default='wlan0',
        max_length=255,
        help_text=("Attacking machine's interface that is on the victim's "
                   "network.")
    )

    state = models.CharField(
        default='discovered',
        max_length=255,
        help_text=("The state of the attack. Possible values are"
                   "'discovered', 'completed', 'running', 'paused' ")
    )

    attacked_at = models.DateTimeField(
        default=timezone.now,
        max_length=255,
        help_text=("The start time of the attack")
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
