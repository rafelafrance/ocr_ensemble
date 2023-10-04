"""Test the distance function in the line_align module."""
import unittest

import cppimport.import_hook  # noqa: F401

from ensemble.pylib.builder.line_align import line_align_py


class TestDistanceAll(unittest.TestCase):
    def setUp(self):
        self.line = line_align_py.LineAlign()

    def test_distance_all_01(self):
        self.assertEqual(self.line.levenshtein_all(["aa", "bb"]), [(2, 0, 1)])

    def test_distance_all_02(self):
        self.assertEqual(
            self.line.levenshtein_all(["aa", "bb", "ab"]),
            [(1, 0, 2), (1, 1, 2), (2, 0, 1)],
        )

    def test_distance_all_03(self):
        self.assertEqual(
            self.line.levenshtein_all(
                [
                    "MOJAVE DESERT, PROVIDENCE MTS.: canyon above",
                    "E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above",
                    "E MOJAVE DESERT PROVTDENCE MTS. # canyon above",
                    "Be ‘MOJAVE DESERT, PROVIDENCE canyon “above",
                ]
            ),
            [(6, 0, 1), (6, 0, 2), (6, 1, 2), (11, 0, 3), (13, 1, 3), (13, 2, 3)],
        )
