from unittest import TestCase

from voicebox.effects.eq import BandPassFilter


class BandPassFilterTest(TestCase):
    def setUp(self):
        # low=900 and high=1100 ==> center=1000 and BW = 200
        self.filter = BandPassFilter(900., 1100.)

    def test_get_center_freq(self):
        self.assertAlmostEqual(1000., self.filter.center_freq)

    def test_get_bandwidth(self):
        self.assertAlmostEqual(200., self.filter.bandwidth)

    def test_set_center_freq(self):
        self.filter.center_freq = 500.
        self.assertAlmostEqual(400., self.filter.low_freq)
        self.assertAlmostEqual(600., self.filter.high_freq)
        self.assertAlmostEqual(200., self.filter.bandwidth)

    def test_set_bandwidth(self):
        self.filter.bandwidth = 400.
        self.assertAlmostEqual(800., self.filter.low_freq)
        self.assertAlmostEqual(1200., self.filter.high_freq)
        self.assertAlmostEqual(1000., self.filter.center_freq)
