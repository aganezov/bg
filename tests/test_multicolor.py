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
        mc1 = Multicolor("red", "red", "blue")
        mc2 = Multicolor("red", "blue")
        self.assertNotEqual(mc1, mc2)

    def test_update(self):
        mc = Multicolor()
        self.assertSetEqual(set(), mc.colors)
        mc.update("red")
        self.assertEqual(len(mc.colors), 1)
        self.assertSetEqual({"red"}, mc.colors)
        mc.update("green", "blue")
        self.assertEqual(len(mc.colors), 3)
        self.assertSetEqual({"red", "blue", "green"}, mc.colors)
        mc.update("red")
        self.assertEqual(len(mc.colors), 3)
        self.assertSetEqual({"red", "blue", "green"}, mc.colors)

    def test_left_merge(self):
        mc1 = Multicolor("red")
        mc2 = Multicolor("blue")
        Multicolor.left_merge(mc1, mc2)
        self.assertEqual(len(mc1.colors), 2)
        self.assertSetEqual({"red", "blue"}, mc1.colors)
        self.assertEqual(len(mc2.colors), 1)
        self.assertSetEqual({"blue"}, mc2.colors)
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
        self.assertSetEqual({"red", "blue"}, mc3.colors)
        mc4 = Multicolor.merge(Multicolor(), mc2)
        self.assertEqual(mc2, mc4)
        mc5 = Multicolor.merge(mc1, mc2, mc3)
        self.assertEqual(mc5, mc3)
        mc6 = Multicolor.merge(mc1)
        self.assertEqual(mc1, mc6)

    def test_inplace_delete(self):
        mc1 = Multicolor("red", "blue", "green")
        mc1.delete(("red",))
        self.assertTrue("red" not in mc1.colors)
        self.assertEqual(len(mc1.colors), 2)
        self.assertSetEqual({"blue", "green"}, mc1.colors)
        mc1.delete(("yellow",))
        self.assertTrue("red" not in mc1.colors)
        self.assertEqual(len(mc1.colors), 2)
        self.assertSetEqual({"blue", "green"}, mc1.colors)
        mc2 = Multicolor("red", "green", "blue")
        mc3 = Multicolor("red", "green", "yellow")
        mc2.delete(mc3)
        self.assertEqual(len(mc2.colors), 1)
        self.assertSetEqual({"blue"}, mc2.colors)

    def test__sub__(self):
        mc1 = Multicolor("red", "blue", "green")
        mc2 = Multicolor("blue", "green", "yellow")
        mc3 = mc1 - mc2
        self.assertEqual(len(mc3.colors), 1)
        self.assertSetEqual({"red"}, mc3.colors)
        mc4 = Multicolor() - mc2
        self.assertEqual(mc4, Multicolor())
        with self.assertRaises(TypeError):
            mc1 - 5

    def test__isub__(self):
        mc1 = Multicolor("red", "blue", "green")
        mc2 = Multicolor("blue", "green", "yellow")
        mc1_id = id(mc1)
        mc1 -= mc2
        self.assertEqual(len(mc1.colors), 1)
        self.assertSetEqual({"red"}, mc1.colors)
        self.assertEqual(id(mc1), mc1_id)

    def test__add__(self):
        mc1 = Multicolor("red", "green")
        mc2 = Multicolor("blue", "yellow", "red")
        mc3 = mc1 + mc2
        self.assertEqual(len(mc3.colors), 4)
        self.assertSetEqual({"red", "green", "blue", "yellow"}, mc3.colors)
        with self.assertRaises(TypeError):
            mc1 + 5

    def test_iadd__(self):
        mc1 = Multicolor("red", "green")
        mc2 = Multicolor("blue", "yellow", "red")
        mc1_id = id(mc1)
        mc1 += mc2
        self.assertEqual(len(mc1.colors), 4)
        self.assertSetEqual({"red", "green", "blue", "yellow"}, mc1.colors)
        self.assertEqual(mc1_id, id(mc1))
        with self.assertRaises(TypeError):
            mc1 + 5

if __name__ == '__main__':
    unittest.main()
