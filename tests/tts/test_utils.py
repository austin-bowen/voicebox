import unittest

from voicebox.tts.utils import add_optional_items


class AddOptionalItemsTest(unittest.TestCase):
    def test(self):
        d = {'foo': 1}

        add_optional_items(d, [('bar', None), ('baz', 3)])

        self.assertDictEqual({'foo': 1, 'baz': 3}, d)
