# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.multicolor import Multicolor


class MulticolorTestCase(unittest.TestCase):
    def test_empty_initialization(self):
        mc = Multicolor()
        self.assertEqual(len(mc.colors), 0)

    def test_single_initialization(self):
        mc = Multicolor("red")
        self.assertEqual(len(mc.colors), 1)
        self.assertSetEqual({"red"}, mc.colors)

    def test_multiple_initialization(self):
        mc = Multicolor("red", "blue", "green")
        self.assertEqual(len(mc.colors), 3)
        self.assertSetEqual({"red", "green", "blue"}, mc.colors)
        mc = Multicolor(*["red", "blue", "green"])
        self.assertEqual(len(mc.colors), 3)
        self.assertSetEqual({"red", "green", "blue"}, mc.colors)

    def test_equality(self):
        mc1 = Multicolor("red")
        mc2 = Multicolor("red")
        self.assertEqual(mc1, mc2)
        mc1 = Multicolor("red", "green")
        mc2 = Multicolor("green", "red")
        self.assertEqual(mc1, mc2)
        mc1 = Multicolor("red")
        mc2 = Multicolor("ret")
        self.assertNotEqual(mc1, mc2)


if __name__ == '__main__':
    unittest.main()
