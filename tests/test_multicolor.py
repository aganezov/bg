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
        self.assertEqual(len(mc.multicolors), 0)

    def test_single_initialization(self):
        mc = Multicolor("red")
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertSetEqual({"red"}, mc.colors)
        self.assertEqual(mc.multicolors["red"], 1)

    def test_multiple_initialization(self):
        mc = Multicolor("red", "blue", "green")
        self.assertEqual(len(mc.colors), 3)
        self.assertEqual(len(mc.multicolors), 3)
        self.assertSetEqual({"red", "green", "blue"}, mc.colors)
        for color in mc.multicolors:
            self.assertEqual(mc.multicolors[color], 1)
        mc = Multicolor(*["red", "blue", "green"])
        self.assertEqual(len(mc.colors), 3)
        self.assertEqual(len(mc.multicolors), 3)
        self.assertSetEqual({"red", "green", "blue"}, mc.colors)
        for color in mc.multicolors:
            self.assertEqual(mc.multicolors[color], 1)
        mc1 = Multicolor("red", "green", "red")
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(mc1.multicolors["green"], 1)
        self.assertEqual(mc1.multicolors["red"], 2)

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
        mc1 = Multicolor("red", "red", "blue")
        mc2 = Multicolor("red", "blue")
        self.assertNotEqual(mc1, mc2)

    def test_update(self):
        mc = Multicolor()
        self.assertSetEqual(set(), mc.colors)
        mc.update("red")
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertSetEqual({"red"}, mc.colors)
        mc.update("green", "blue")
        self.assertEqual(len(mc.colors), 3)
        self.assertEqual(len(mc.multicolors), 3)
        self.assertSetEqual({"red", "blue", "green"}, mc.colors)
        for color in mc.multicolors:
            self.assertEqual(mc.multicolors[color], 1)
        mc.update("red")
        self.assertEqual(len(mc.colors), 3)
        self.assertEqual(len(mc.multicolors), 3)
        for color in mc.multicolors:
            if color == "red":
                self.assertEqual(mc.multicolors[color], 2)
            else:
                self.assertEqual(mc.multicolors[color], 1)
        self.assertSetEqual({"red", "blue", "green"}, mc.colors)

    def test_left_merge(self):
        mc1 = Multicolor("red")
        mc2 = Multicolor("blue")
        Multicolor.left_merge(mc1, mc2)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        for color in mc1.multicolors:
            self.assertEqual(mc1.multicolors[color], 1)
        self.assertSetEqual({"red", "blue"}, mc1.colors)
        self.assertEqual(len(mc2.colors), 1)
        self.assertEqual(len(mc2.multicolors), 1)
        self.assertSetEqual({"blue"}, mc2.colors)
        for color in mc2.multicolors:
            self.assertEqual(mc2.multicolors[color], 1)
        mc3 = Multicolor.left_merge(Multicolor(), mc2)
        self.assertEqual(mc3, mc2)
        mc4 = Multicolor.left_merge(mc2, Multicolor())
        self.assertEqual(mc4, mc2)

    def test_merge(self):
        mc1 = Multicolor("red")
        mc2 = Multicolor("blue")
        mc3 = Multicolor.merge(mc1, mc2)
        self.assertNotEqual(mc1, mc3)
        self.assertNotEqual(mc2, mc3)
        self.assertEqual(len(mc3.colors), 2)
        self.assertEqual(len(mc3.multicolors), 2)
        for color in mc3.multicolors:
            self.assertEqual(mc3.multicolors[color], 1)
        self.assertSetEqual({"red", "blue"}, mc3.colors)
        mc4 = Multicolor.merge(Multicolor(), mc2)
        self.assertEqual(mc2, mc4)
        mc5 = Multicolor.merge(mc1, mc2, mc3)
        self.assertNotEqual(mc5, mc3)
        self.assertEqual(len(mc5.colors), 2)
        for color in mc5.multicolors:
            self.assertEqual(mc5.multicolors[color], 2)
        mc6 = Multicolor.merge(mc1)
        self.assertEqual(mc1, mc6)

    def test_inplace_delete(self):
        mc1 = Multicolor("red", "blue", "green")
        mc1.delete(("red",))
        self.assertTrue("red" not in mc1.colors)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertSetEqual({"blue", "green"}, mc1.colors)
        for color in mc1.multicolors:
            self.assertEqual(mc1.multicolors[color], 1)
        mc1.delete(("yellow",))
        self.assertTrue("red" not in mc1.colors)
        self.assertEqual(len(mc1.colors), 2)
        self.assertSetEqual({"blue", "green"}, mc1.colors)
        self.assertEqual(len(mc1.multicolors), 2)
        for color in mc1.multicolors:
            self.assertEqual(mc1.multicolors[color], 1)
        mc2 = Multicolor("red", "green", "blue")
        mc3 = Multicolor("red", "green", "yellow")
        mc2.delete(mc3)
        self.assertEqual(len(mc2.colors), 1)
        self.assertEqual(len(mc2.multicolors), 1)
        self.assertSetEqual({"blue"}, mc2.colors)
        for color in mc2.multicolors:
            self.assertEqual(mc2.multicolors[color], 1)
        mc4 = Multicolor("red", "red", "green", "blue")
        mc5 = Multicolor("red", "green", "yellow")
        mc4.delete(mc5)
        self.assertEqual(len(mc4.colors), 2)
        self.assertEqual(len(mc4.multicolors), 2)
        self.assertSetEqual({"blue", "red"}, mc4.colors)
        for color in mc4.multicolors:
            self.assertEqual(mc4.multicolors[color], 1)

    def test__sub__(self):
        mc1 = Multicolor("red", "blue", "red", "green")
        mc2 = Multicolor("blue", "green", "yellow")
        mc3 = mc1 - mc2
        self.assertEqual(len(mc3.colors), 1)
        self.assertEqual(len(mc3.multicolors), 1)
        self.assertEqual(mc3.multicolors["red"], 2)
        self.assertSetEqual({"red"}, mc3.colors)
        mc4 = Multicolor() - mc2
        self.assertEqual(mc4, Multicolor())
        with self.assertRaises(TypeError):
            mc1 - 5

    def test__isub__(self):
        mc1 = Multicolor("red", "blue", "red", "green")
        mc2 = Multicolor("blue", "green", "yellow")
        mc1_id = id(mc1)
        mc1 -= mc2
        self.assertEqual(len(mc1.colors), 1)
        self.assertEqual(len(mc1.multicolors), 1)
        self.assertEqual(mc1.multicolors["red"], 2)
        self.assertSetEqual({"red"}, mc1.colors)
        self.assertEqual(id(mc1), mc1_id)

    def test__add__(self):
        mc1 = Multicolor("red", "green")
        mc2 = Multicolor("blue", "yellow", "red")
        mc3 = mc1 + mc2
        self.assertEqual(len(mc3.colors), 4)
        self.assertEqual(len(mc3.multicolors), 4)
        self.assertSetEqual({"red", "green", "blue", "yellow"}, mc3.colors)
        for color in mc3.multicolors:
            if color == "red":
                self.assertEqual(mc3.multicolors[color], 2)
            else:
                self.assertEqual(mc3.multicolors[color], 1)
        with self.assertRaises(TypeError):
            mc1 + 5

    def test_iadd__(self):
        mc1 = Multicolor("red", "green")
        mc2 = Multicolor("blue", "yellow", "red")
        mc1_id = id(mc1)
        mc1 += mc2
        self.assertEqual(len(mc1.colors), 4)
        self.assertEqual(len(mc1.multicolors), 4)
        self.assertSetEqual({"red", "green", "blue", "yellow"}, mc1.colors)
        for color in mc1.multicolors:
            if color == "red":
                self.assertEqual(mc1.multicolors[color], 2)
            else:
                self.assertEqual(mc1.multicolors[color], 1)
        self.assertEqual(mc1_id, id(mc1))
        with self.assertRaises(TypeError):
            mc1 + 5

if __name__ == '__main__':
    unittest.main()
