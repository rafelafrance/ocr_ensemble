import unittest

import numpy as np

import ensemble.pylib.builder.line_align.char_sub_matrix as sub


class TestCharSubMatrix(unittest.TestCase):
    def test_get_max_iou_01(self):
        pix1 = np.array(
            [
                [0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0],
            ]
        )
        pix2 = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ]
        )
        self.assertEqual(sub.get_max_iou(pix1, pix2), 1.0)

    def test_get_max_iou_02(self):
        pix1 = np.array(
            [
                [0.0, 0.0, 0.0],
                [0.0, 1.0, 1.0],
                [0.0, 0.0, 0.0],
            ]
        )
        pix2 = np.array(
            [
                [1.0, 1.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ]
        )
        self.assertEqual(sub.get_max_iou(pix1, pix2), 1.0)

    def test_get_max_iou_03(self):
        pix1 = np.array(
            [
                [0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
            ]
        )
        pix2 = np.array(
            [
                [1.0, 1.0, 1.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ]
        )
        self.assertEqual(sub.get_max_iou(pix1, pix2), 0.2)
