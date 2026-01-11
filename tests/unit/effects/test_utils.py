from math import inf
from unittest import TestCase

from parameterized import parameterized

from voicebox.effects.utils import db


class DbTest(TestCase):
    @parameterized.expand(
        [
            (-inf, 0.0),
            (-20.0, 0.100),
            (-6.0, 0.501),
            (0.0, 1.000),
            (+6.0, 1.995),
            (+20.0, 10.00),
            (+inf, inf),
        ]
    )
    def test_db(self, db_: float, expected: float):
        self.assertAlmostEqual(expected, db(db_), places=3)
