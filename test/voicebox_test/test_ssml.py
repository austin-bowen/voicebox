import unittest

from parameterized import parameterized

from voicebox.ssml import SSML


class SSMLTest(unittest.TestCase):
    @parameterized.expand([
        ('This is not SSML.', False),
        ('', False),
        ('<speak>This is SSML.</speak>', True),
        ('  \t\r\n   <speak>       This is also SSML.      </speak>', True),
    ])
    def test_auto(self, text: str, is_ssml: bool):
        result = SSML.auto(text)

        self.assertEqual(text, result)
        self.assertIsInstance(result, str)

        if is_ssml:
            self.assertIsInstance(result, SSML)
        else:
            self.assertNotIsInstance(result, SSML)
