import time
import unittest
from unittest.mock import Mock, call

from parameterized import parameterized

from tests.utils import assert_called_with_exactly
from voicebox.voiceboxes.parallel import VoiceboxThread


class VoiceboxThreadTest(unittest.TestCase):
    def setUp(self):
        self.mock_voicebox = Mock()
        self.mock_voicebox.say.side_effect = lambda t: None

        self.voicebox = VoiceboxThread(self.mock_voicebox)

    def tearDown(self):
        self.voicebox.stop()

    def test_constructor_defaults(self):
        self.assertIs(self.voicebox.voicebox, self.mock_voicebox)
        self.assertAlmostEqual(1., self.voicebox.queue_get_timeout)
        self.assertEqual('Voicebox', self.voicebox.name)
        self.assertTrue(self.voicebox.daemon)

        time.sleep(0.1)
        self.assertTrue(self.voicebox.is_alive())

        self.mock_voicebox.say.assert_not_called()

    def test_constructor(self):
        voicebox = VoiceboxThread(
            self.mock_voicebox,
            start=False,
            queue_get_timeout=3.14,
            name='foo',
            daemon=False,
        )

        self.assertIs(voicebox.voicebox, self.mock_voicebox)
        self.assertAlmostEqual(3.14, voicebox.queue_get_timeout)
        self.assertEqual('foo', voicebox.name)
        self.assertFalse(voicebox.daemon)

        time.sleep(0.1)
        self.assertFalse(voicebox.is_alive())

        self.mock_voicebox.say.assert_not_called()

    def test_say(self):
        self.voicebox.say('foo')
        self.voicebox.wait_until_done()

        self.mock_voicebox.say.assert_called_once_with('foo')

    def test_say_all(self):
        self.voicebox.say_all(['foo', 'bar'])
        self.voicebox.wait_until_done()

        assert_called_with_exactly(
            self.mock_voicebox.say,
            [call('foo'), call('bar')],
        )

    @parameterized.expand([True, False])
    def test_stop(self, wait: bool):
        self.assertTrue(self.voicebox.is_alive())

        self.voicebox.stop(wait=wait)

        if not wait:
            self.voicebox.join()

        self.assertFalse(self.voicebox.is_alive())
