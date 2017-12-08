from mock import patch
from django.utils import timezone
from django.test import TestCase
from breach.strategy import Strategy
from breach.models import Target, Victim, SampleSet


class ErrorHandlingTestCase(TestCase):
    def setUp(self):
        self.target = Target.objects.create(
            endpoint='https://di.uoa.gr/?breach=%s',
            prefix='test',
            alphabet='01',
            secretlength=5,
            recordscardinality=1,
            samplesize=2
        )

        self.victim = Victim.objects.create(
            target=self.target,
            sourceip='192.168.10.140',
            snifferendpoint='http://localhost/',
            recordscardinality=1
        )

    def tearDown(self):
        for sampleset in SampleSet.objects.all():
            sampleset.completed = timezone.now()
            sampleset.save()

    @patch('breach.strategy.Sniffer')
    def test_calibration(self, Sniffer):
        capture0 = {'data': 'bigbignextround', 'records': 3}
        instance = Sniffer.return_value
        instance.read.return_value = capture0

        for _ in range(3):
            strategy = Strategy(self.victim)
            strategy.get_work()
            res = strategy.work_completed()
            self.assertTrue(not res)

        self.assertEqual(self.victim.calibration_wait, 0.1)

    @patch('breach.strategy.Sniffer')
    def test_cardinality(self, Sniffer):
        capture = {'data': 'bigbignextround', 'records': 2}
        instance = Sniffer.return_value
        instance.read.return_value = capture

        strategy = Strategy(self.victim)
        strategy.get_work()
        res = strategy.work_completed()
        self.assertTrue(not res)

        capture = {'data': 'bigbignextround', 'records': 4}
        instance = Sniffer.return_value
        instance.read.return_value = capture

        for _ in range(4):
            strategy = Strategy(self.victim)
            strategy.get_work()
            res = strategy.work_completed()
            self.assertTrue(not res)

        self.assertEqual(self.victim.recordscardinality, 2)
        self.assertEqual(self.target.recordscardinality, 2)

    @patch('breach.strategy.Sniffer')
    def test_success_error(self, Sniffer):
        capture = {'data': 'bigbignextround', 'records': 2}
        instance = Sniffer.return_value
        instance.read.return_value = capture

        strategy = Strategy(self.victim)
        strategy.get_work()
        res = strategy.work_completed(False)
        self.assertTrue(not res)
