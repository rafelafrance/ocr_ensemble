"""Test the levenshtein function in the line_align module."""
import unittest

import cppimport.import_hook  # noqa: F401

from ensemble.pylib.builder.line_align import line_align_py


class TestDistance(unittest.TestCase):
    def setUp(self):
        self.line = line_align_py.LineAlign()

    def test_distance_01(self):
        self.assertEqual(self.line.levenshtein("aa", "bb"), 2)

    def test_distance_02(self):
        self.assertEqual(self.line.levenshtein("ab", "bb"), 1)

    def test_distance_03(self):
        self.assertEqual(self.line.levenshtein("ab", "ab"), 0)

    def test_distance_04(self):
        self.assertEqual(self.line.levenshtein("aa", "aba"), 1)

    def test_distance_05(self):
        self.assertEqual(self.line.levenshtein("aa", "baa"), 1)

    def test_distance_06(self):
        self.assertEqual(self.line.levenshtein("aa", "aab"), 1)

    def test_distance_07(self):
        self.assertEqual(self.line.levenshtein("baa", "aa"), 1)

    def test_distance_08(self):
        self.assertEqual(self.line.levenshtein("aab", "aa"), 1)

    def test_distance_09(self):
        self.assertEqual(self.line.levenshtein("baab", "aa"), 2)

    def test_distance_10(self):
        self.assertEqual(self.line.levenshtein("aa", "baab"), 2)

    def test_distance_11(self):
        self.assertEqual(self.line.levenshtein("", "aa"), 2)

    def test_distance_12(self):
        self.assertEqual(self.line.levenshtein("aa", ""), 2)

    def test_distance_13(self):
        self.assertEqual(self.line.levenshtein("", ""), 0)

    def test_distance_14(self):
        self.assertEqual(1, self.line.levenshtein("aa", "五aa"))

    def test_distance_15(self):
        self.assertEqual(1, self.line.levenshtein("五aa", "aa"))

    def test_distance_16(self):
        self.assertEqual(1, self.line.levenshtein("aa", "aa五"))

    def test_distance_17(self):
        self.assertEqual(1, self.line.levenshtein("aa五", "aa"))

    def test_distance_18(self):
        self.assertEqual(1, self.line.levenshtein("a五a", "aa"))

    def test_distance_19(self):
        self.assertEqual(1, self.line.levenshtein("aa", "a五a"))

    def test_distance_20(self):
        self.assertEqual(1, self.line.levenshtein("五五", "五六"))

    def test_distance_21(self):
        self.assertEqual(0, self.line.levenshtein("五五", "五五"))

    def test_distance_22(self):
        self.assertEqual(self.line.levenshtein("123aa4", "aa"), 4)

    def test_distance_23(self):
        self.assertEqual(self.line.levenshtein("aa", "1aa234"), 4)

    def test_distance_24(self):
        self.assertEqual(self.line.levenshtein("aa", "a123a"), 3)

    def test_distance_25(self):
        self.assertEqual(self.line.levenshtein("aa", "12345aa"), 5)

    def test_distance_26(self):
        self.assertEqual(
            self.line.levenshtein(
                "Commelinaceae Commelina virginica", "Commelina virginica"
            ),
            14,
        )

    def test_distance_27(self):
        self.assertEqual(
            self.line.levenshtein(
                "North Carolina NORTH CAROLINA Guilford County",
                "North Carolina OT CAROLINA Guilford County",
            ),
            3,
        )
