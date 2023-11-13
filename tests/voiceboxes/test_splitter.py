import unittest
from typing import List
from unittest import TestCase

from parameterized import parameterized

from voicebox.ssml import SSML
from voicebox.voiceboxes.splitter import SimpleSentenceSplitter, PunktSentenceSplitter

commonly_handled_sentences = [
    ('', []),
    ('Hello, world!', ['Hello, world!']),
    ('this has no punctuation', ['this has no punctuation']),
    # Handles all three basic English punctuations
    ('First sentence. Second sentence! Third sentence?', ['First sentence.', 'Second sentence!', 'Third sentence?']),
    # Handles decimal numbers
    ('pi = 3.14. Do you want some pie?', ['pi = 3.14.', 'Do you want some pie?']),
    # Does not split SSML
    (SSML('<speak>This is SSML. Do not split.</speak>'), [SSML('<speak>This is SSML. Do not split.</speak>')]),
]


class SimpleSentenceSplitterTest(TestCase):
    def setUp(self):
        self.splitter = SimpleSentenceSplitter()

    @parameterized.expand(commonly_handled_sentences + [
        # Splits on ellipses
        ('Well... that is interesting.', ['Well...', 'that is interesting.']),
        # Does not handle abbreviations :(
        ('Mr. Jones went to see Dr. Sherman.', ['Mr.', 'Jones went to see Dr.', 'Sherman.']),
    ])
    def test_split(self, text: str, expected: List[str]):
        actual = list(self.splitter.split(text))
        self.assertListEqual(expected, actual)


class PunktSentenceSplitterTest(TestCase):
    def setUp(self):
        self.splitter = PunktSentenceSplitter()

    @parameterized.expand(commonly_handled_sentences + [
        # Does not split on ellipses
        ('Well... that is interesting.', ['Well... that is interesting.']),
        # Handles mid-sentence punctuation
        ('Mr. Jones went to see Dr. Sherman.', ['Mr. Jones went to see Dr. Sherman.']),
    ])
    def test_split(self, text: str, expected: List[str]):
        actual = list(self.splitter.split(text))
        self.assertListEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
