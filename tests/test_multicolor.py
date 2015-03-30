# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest
from bg.multicolor import Multicolor
from bg.genome import BGGenome


class MulticolorTestCase(unittest.TestCase):
    def setUp(self):
        self.genome1 = BGGenome("red")
        self.genome2 = BGGenome("green")
        self.genome3 = BGGenome("blue")
        self.genome4 = BGGenome("black")
        self.genome5 = BGGenome("yellow")

    def test_empty_initialization(self):
        mc = Multicolor()
        self.assertEqual(len(mc.colors), 0)
        self.assertEqual(len(mc.multicolors), 0)

    def test_single_initialization(self):
        mc = Multicolor(self.genome1)
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertSetEqual({self.genome1}, mc.colors)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        mc = Multicolor(self.genome1)
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertSetEqual({self.genome1}, mc.colors)
        self.assertEqual(mc.multicolors[self.genome1], 1)

    def test_multiple_initialization(self):
        mc = Multicolor(self.genome1, self.genome2, self.genome3)
        self.assertEqual(len(mc.colors), 3)
        self.assertEqual(len(mc.multicolors), 3)
        self.assertSetEqual({self.genome1, self.genome2, self.genome3}, mc.colors)
        for color in mc.multicolors:
            self.assertEqual(mc.multicolors[color], 1)
        mc = Multicolor(*[self.genome1, self.genome2, self.genome3])
        self.assertEqual(len(mc.colors), 3)
        self.assertEqual(len(mc.multicolors), 3)
        self.assertSetEqual({self.genome1, self.genome2, self.genome3}, mc.colors)
        for color in mc.multicolors:
            self.assertEqual(mc.multicolors[color], 1)
        mc1 = Multicolor(self.genome1, self.genome2, self.genome1)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(mc1.multicolors[self.genome2], 1)
        self.assertEqual(mc1.multicolors[self.genome1], 2)

    def test_equality(self):
        mc1 = Multicolor(self.genome1)
        mc2 = Multicolor(self.genome1)
        self.assertEqual(mc1, mc2)
        mc1 = Multicolor(self.genome1, self.genome2)
        mc2 = Multicolor(self.genome2, self.genome1)
        self.assertEqual(mc1, mc2)
        mc1 = Multicolor(self.genome1)
        mc2 = Multicolor(BGGenome("ret"))
        self.assertNotEqual(mc1, mc2)
        mc1 = Multicolor(self.genome1, self.genome1, self.genome3)
        mc2 = Multicolor(self.genome1, self.genome3)
        self.assertNotEqual(mc1, mc2)

    def test_update(self):
        mc = Multicolor()
        self.assertSetEqual(set(), mc.colors)
        mc.update(self.genome1)
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertSetEqual({self.genome1}, mc.colors)
        mc.update(self.genome2, self.genome3)
        self.assertEqual(len(mc.colors), 3)
        self.assertEqual(len(mc.multicolors), 3)
        self.assertSetEqual({self.genome1, self.genome2, self.genome3}, mc.colors)
        for color in mc.multicolors:
            self.assertEqual(mc.multicolors[color], 1)
        mc.update(self.genome1)
        self.assertEqual(len(mc.colors), 3)
        self.assertEqual(len(mc.multicolors), 3)
        for color in mc.multicolors:
            if color == self.genome1:
                self.assertEqual(mc.multicolors[color], 2)
            else:
                self.assertEqual(mc.multicolors[color], 1)
        self.assertSetEqual({self.genome1, self.genome2, self.genome3}, mc.colors)

    def test_left_merge(self):
        mc1 = Multicolor(self.genome1)
        mc2 = Multicolor(self.genome3)
        Multicolor.left_merge(mc1, mc2)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        for color in mc1.multicolors:
            self.assertEqual(mc1.multicolors[color], 1)
        self.assertSetEqual({self.genome1, self.genome3}, mc1.colors)
        self.assertEqual(len(mc2.colors), 1)
        self.assertEqual(len(mc2.multicolors), 1)
        self.assertSetEqual({self.genome3}, mc2.colors)
        for color in mc2.multicolors:
            self.assertEqual(mc2.multicolors[color], 1)
        mc3 = Multicolor.left_merge(Multicolor(), mc2)
        self.assertEqual(mc3, mc2)
        mc4 = Multicolor.left_merge(mc2, Multicolor())
        self.assertEqual(mc4, mc2)

    def test_merge(self):
        mc1 = Multicolor(self.genome1)
        mc2 = Multicolor(self.genome3)
        mc3 = Multicolor.merge(mc1, mc2)
        self.assertNotEqual(mc1, mc3)
        self.assertNotEqual(mc2, mc3)
        self.assertEqual(len(mc3.colors), 2)
        self.assertEqual(len(mc3.multicolors), 2)
        for color in mc3.multicolors:
            self.assertEqual(mc3.multicolors[color], 1)
        self.assertSetEqual({self.genome1, self.genome3}, mc3.colors)
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
        mc1 = Multicolor(self.genome1, self.genome3, self.genome2)
        mc1.delete((self.genome1,))
        self.assertTrue(self.genome1 not in mc1.colors)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertSetEqual({self.genome3, self.genome2}, mc1.colors)
        for color in mc1.multicolors:
            self.assertEqual(mc1.multicolors[color], 1)
        mc1.delete((self.genome5,))
        self.assertTrue(self.genome1 not in mc1.colors)
        self.assertEqual(len(mc1.colors), 2)
        self.assertSetEqual({self.genome3, self.genome2}, mc1.colors)
        self.assertEqual(len(mc1.multicolors), 2)
        for color in mc1.multicolors:
            self.assertEqual(mc1.multicolors[color], 1)
        mc2 = Multicolor(self.genome1, self.genome2, self.genome3)
        mc3 = Multicolor(self.genome1, self.genome2, self.genome5)
        mc2.delete(mc3)
        self.assertEqual(len(mc2.colors), 1)
        self.assertEqual(len(mc2.multicolors), 1)
        self.assertSetEqual({self.genome3}, mc2.colors)
        for color in mc2.multicolors:
            self.assertEqual(mc2.multicolors[color], 1)
        mc4 = Multicolor(self.genome1, self.genome1, self.genome2, self.genome3)
        mc5 = Multicolor(self.genome1, self.genome2, self.genome5)
        mc4.delete(mc5)
        self.assertEqual(len(mc4.colors), 2)
        self.assertEqual(len(mc4.multicolors), 2)
        self.assertSetEqual({self.genome3, self.genome1}, mc4.colors)
        for color in mc4.multicolors:
            self.assertEqual(mc4.multicolors[color], 1)

    def test__sub__(self):
        mc1 = Multicolor(self.genome1, self.genome3, self.genome1, self.genome2)
        mc2 = Multicolor(self.genome3, self.genome2, self.genome5)
        mc3 = mc1 - mc2
        self.assertEqual(len(mc3.colors), 1)
        self.assertEqual(len(mc3.multicolors), 1)
        self.assertEqual(mc3.multicolors[self.genome1], 2)
        self.assertSetEqual({self.genome1}, mc3.colors)
        mc4 = Multicolor() - mc2
        self.assertEqual(mc4, Multicolor())
        with self.assertRaises(TypeError):
            mc1 - 5

    def test__isub__(self):
        mc1 = Multicolor(self.genome1, self.genome3, self.genome1, self.genome2)
        mc2 = Multicolor(self.genome3, self.genome2, self.genome5)
        mc1_id = id(mc1)
        mc1 -= mc2
        self.assertEqual(len(mc1.colors), 1)
        self.assertEqual(len(mc1.multicolors), 1)
        self.assertEqual(mc1.multicolors[self.genome1], 2)
        self.assertSetEqual({self.genome1}, mc1.colors)
        self.assertEqual(id(mc1), mc1_id)
        with self.assertRaises(TypeError):
            mc1 -= 5

    def test__add__(self):
        mc1 = Multicolor(self.genome1, self.genome2)
        mc2 = Multicolor(self.genome3, self.genome5, self.genome1)
        mc3 = mc1 + mc2
        self.assertEqual(len(mc3.colors), 4)
        self.assertEqual(len(mc3.multicolors), 4)
        self.assertSetEqual({self.genome1, self.genome2, self.genome3, self.genome5}, mc3.colors)
        for color in mc3.multicolors:
            if color == self.genome1:
                self.assertEqual(mc3.multicolors[color], 2)
            else:
                self.assertEqual(mc3.multicolors[color], 1)
        with self.assertRaises(TypeError):
            mc1 + 5

    def test_iadd__(self):
        mc1 = Multicolor(self.genome1, self.genome2)
        mc2 = Multicolor(self.genome3, self.genome5, self.genome1)
        mc1_id = id(mc1)
        mc1 += mc2
        self.assertEqual(len(mc1.colors), 4)
        self.assertEqual(len(mc1.multicolors), 4)
        self.assertSetEqual({self.genome1, self.genome2, self.genome3, self.genome5}, mc1.colors)
        for color in mc1.multicolors:
            if color == self.genome1:
                self.assertEqual(mc1.multicolors[color], 2)
            else:
                self.assertEqual(mc1.multicolors[color], 1)
        self.assertEqual(mc1_id, id(mc1))
        with self.assertRaises(TypeError):
            mc1 += 5

    def test__lt__and__le__(self):
        mc1 = Multicolor(self.genome1, self.genome2, self.genome1)
        mc2 = Multicolor(self.genome1, self.genome2)
        self.assertTrue(mc2 < mc1)
        self.assertTrue(mc2 <= mc1)
        self.assertFalse(mc2 <= 5)
        self.assertFalse(mc2 < 5)
        mc2 = Multicolor(self.genome1, self.genome1, self.genome2)
        self.assertFalse(mc2 < mc1)
        self.assertTrue(mc2 <= mc1)
        mc2 = Multicolor(self.genome1, self.genome1, self.genome2, self.genome2)
        self.assertFalse(mc2 < mc1)
        self.assertFalse(mc2 <= mc1)

    def test__gt__and__ge__(self):
        mc1 = Multicolor(self.genome1, self.genome2, self.genome1)
        mc2 = Multicolor(self.genome1, self.genome2)
        self.assertTrue(mc1 > mc2)
        self.assertTrue(mc1 >= mc2)
        mc2 = Multicolor(self.genome1, self.genome1, self.genome2)
        self.assertFalse(mc1 > mc2)
        self.assertTrue(mc1 >= mc2)
        mc2 = Multicolor(self.genome1, self.genome1, self.genome2, self.genome2)
        self.assertFalse(mc1 > mc2)
        self.assertFalse(mc1 >= mc2)

    def test_similarity_score(self):
        mc1 = Multicolor(self.genome1, self.genome2)
        mc2 = Multicolor(self.genome1, self.genome2)
        self.assertEqual(Multicolor.similarity_score(mc1, mc2), 2)
        self.assertEqual(Multicolor.similarity_score(mc2, mc1), 2)
        mc2 = Multicolor(self.genome1, self.genome1)
        self.assertEqual(Multicolor.similarity_score(mc1, mc2), 1)
        self.assertEqual(Multicolor.similarity_score(mc2, mc1), 1)
        mc2 = Multicolor(self.genome1)
        self.assertEqual(Multicolor.similarity_score(mc1, mc2), 1)
        self.assertEqual(Multicolor.similarity_score(mc2, mc1), 1)
        mc2 = Multicolor(self.genome4)
        self.assertEqual(Multicolor.similarity_score(mc1, mc2), 0)
        self.assertEqual(Multicolor.similarity_score(mc2, mc1), 0)

    def test_split_colors_simple_multicolor_no_duplications(self):
        # color exists in guidance
        mc = Multicolor(self.genome1)
        guidance = [(self.genome1, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        # color exists in guidance only as subset
        mc = Multicolor(self.genome1)
        guidance = [(self.genome1, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        # color exists in guidance both as subset and a set itself
        mc = Multicolor(self.genome1)
        guidance = [(self.genome1, self.genome4), (self.genome1, ), (self.genome4, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        # color does not exist in guidance
        mc = Multicolor(self.genome1)
        guidance = [(self.genome2, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 1)

    def test_split_colors_simple_multicolor_with_duplications(self):
        # color exists in guidance
        mc = Multicolor(self.genome1, self.genome1)
        guidance = [(self.genome1, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 2)
        mc = Multicolor.split_colors(mc)[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 2)
        # color exists in guidance only as subset
        mc = Multicolor(self.genome1, self.genome1)
        guidance = [(self.genome1, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 2)
        # color exists in guidance both as subset and a set itself
        mc = Multicolor(self.genome1)
        guidance = [(self.genome1, self.genome4), (self.genome1, ), (self.genome4, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        # color does not exist in guidance
        mc = Multicolor(self.genome1, self.genome1)
        guidance = [(self.genome2, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 2)

    def test_split_colors_complex_multicolor_no_duplications(self):
        # full color exists in guidance
        mc = Multicolor(self.genome1, self.genome4)
        guidance = [(self.genome1, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        self.assertEqual(mc.multicolors[self.genome4], 1)
        ################################################################
        guidance = [(self.genome1, ), (self.genome4, ), (self.genome1, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        self.assertEqual(mc.multicolors[self.genome4], 1)
        ################################################################
        guidance = [(self.genome1, ), (self.genome4, ), (self.genome1, self.genome4),
                    (self.genome1, self.genome4, self.genome2), (self.genome2, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        self.assertEqual(mc.multicolors[self.genome4], 1)
        # full color exists in guidance only as subset
        mc = Multicolor(self.genome1, self.genome4)
        guidance = [(self.genome1, self.genome4, self.genome2), (self.genome2, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        self.assertEqual(mc.multicolors[self.genome4], 1)
        # full color exists in guidance both as subset and a set itself
        mc = Multicolor(self.genome1, self.genome4)
        guidance = [(self.genome1, self.genome4, self.genome2), (self.genome2, ), (self.genome1, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        self.assertEqual(mc.multicolors[self.genome4], 1)
        # full color exists in guidance both as subset and portions of it intersect with some guidance subsets
        mc = Multicolor(self.genome1, self.genome4)
        guidance = [(self.genome1, self.genome4, self.genome2), (self.genome4, self.genome2),
                    (self.genome1, self.genome2)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        self.assertEqual(mc.multicolors[self.genome4], 1)
        # color does not exist in guidance (nor any of its subsets by themselves), but it intersects with some
        # guidance sets
        mc = Multicolor(self.genome1, self.genome4)
        guidance = [(self.genome1, self.genome2), (self.genome4, self.genome3)]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 1)
        self.assertEqual(len(mc1.multicolors), 1)
        self.assertEqual(len(mc2.colors), 1)
        self.assertEqual(len(mc2.multicolors), 1)
        # portion of a color exists in guidance as a set, while rest of it is not mentioned
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome2), ]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome4, self.genome3)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists in guidance as subset, while rest of it is not mentioned
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome2, self.genome5), ]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome4, self.genome3)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists in guidance as set, while the rest exists as set
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome2), (self.genome4, self.genome3)]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome4, self.genome3)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists in guidance as subset, while the rest exists as subset
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome2, self.genome5), (self.genome4, self.genome3, self.genome5)]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome4, self.genome3)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists in guidance as set, while the rest exists as subset
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome2), (self.genome4, self.genome3, self.genome5)]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome4, self.genome3)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists as intersections, while the rest exists as set
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome5), (self.genome2, self.genome5), (self.genome4, self.genome3)]
        mc1, mc2, mc3 = Multicolor.split_colors(mc, guidance=guidance)
        multicolors = [Multicolor(self.genome1), Multicolor(self.genome4, self.genome3), Multicolor(self.genome2)]
        for mc in [mc1, mc2, mc3]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists as intersection, while the rest exists as subset
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome5), (self.genome2, self.genome5),
                    (self.genome4, self.genome3, self.genome5)]
        mc1, mc2, mc3 = Multicolor.split_colors(mc, guidance=guidance)
        multicolors = [Multicolor(self.genome1), Multicolor(self.genome4, self.genome3), Multicolor(self.genome2)]
        for mc in [mc1, mc2, mc3]:
            self.assertTrue(mc in multicolors)
        # both portions of color exist as intersections
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome5), (self.genome2, self.genome5), (self.genome4, self.genome5),
                    (self.genome3, self.genome5)]
        mc1, mc2, mc3, mc4 = Multicolor.split_colors(mc, guidance=guidance)
        multicolors = [Multicolor(self.genome1), Multicolor(self.genome4), Multicolor(self.genome2),
                       Multicolor(self.genome3)]
        for mc in [mc1, mc2, mc3, mc4]:
            self.assertTrue(mc in multicolors)
        # color does not exist in guidance
        mc = Multicolor(self.genome1, self.genome4)
        guidance = [(self.genome2, self.genome3), (self.genome2, ), (self.genome3, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 2)
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        self.assertEqual(mc.multicolors[self.genome4], 1)

    def test_split_colors_complex_multicolor_with_duplications(self):
        # full color exists in guidance
        mc = Multicolor(self.genome1, self.genome4, self.genome1, self.genome4)
        guidance = [(self.genome1, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 2)
        self.assertEqual(mc.multicolors[self.genome4], 2)
        ################################################################
        guidance = [(self.genome1, ), (self.genome4, ), (self.genome1, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 2)
        self.assertEqual(mc.multicolors[self.genome4], 2)
        ################################################################
        guidance = [(self.genome1, ), (self.genome4, ), (self.genome1, self.genome4),
                    (self.genome1, self.genome4, self.genome2), (self.genome2, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 2)
        self.assertEqual(mc.multicolors[self.genome4], 2)
        # full color exists in guidance only as subset
        mc = Multicolor(self.genome1, self.genome4, self.genome1, self.genome4, self.genome1)
        guidance = [(self.genome1, self.genome4, self.genome2), (self.genome2, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 3)
        self.assertEqual(mc.multicolors[self.genome4], 2)
        # full color exists in guidance both as subset and a set itself
        mc = Multicolor(self.genome1, self.genome4, self.genome1, self.genome1)
        guidance = [(self.genome1, self.genome4, self.genome2), (self.genome2, ), (self.genome1, self.genome4)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 3)
        self.assertEqual(mc.multicolors[self.genome4], 1)
        # full color exists in guidance both as subset and portions of it intersect with some guidance subsets
        mc = Multicolor(self.genome1, self.genome4, self.genome1, self.genome4)
        guidance = [(self.genome1, self.genome4, self.genome2), (self.genome4, self.genome2),
                    (self.genome1, self.genome2)]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 2)
        self.assertEqual(mc.multicolors[self.genome4], 2)
        # color does not exist in guidance (nor any of its subsets by themselves), but it intersects with some
        # guidance sets
        mc = Multicolor(self.genome1, self.genome4, self.genome1, self.genome4, self.genome1, self.genome4)
        guidance = [(self.genome1, self.genome2), (self.genome4, self.genome3)]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 1)
        self.assertEqual(len(mc1.multicolors), 1)
        self.assertEqual(len(mc2.colors), 1)
        self.assertEqual(len(mc2.multicolors), 1)
        for mc in [mc1, mc2]:
            for color in mc.colors:
                self.assertEqual(mc.multicolors[color], 3)
        # portion of a color exists in guidance as a set, while rest of it is not mentioned
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome2), ]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome4, self.genome3)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists in guidance as subset, while rest of it is not mentioned
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome2, self.genome5), ]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome4, self.genome3)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists in guidance as set, while the rest exists as set
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome2), (self.genome4, self.genome3)]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome4, self.genome3)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists in guidance as subset, while the rest exists as subset
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome2, self.genome5), (self.genome4, self.genome3, self.genome5)]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome4, self.genome3)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists in guidance as set, while the rest exists as subset
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3, self.genome1, self.genome2,
                        self.genome4)
        guidance = [(self.genome1, self.genome2), (self.genome4, self.genome3, self.genome5)]
        mc1, mc2 = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(mc1.colors), 2)
        self.assertEqual(len(mc1.multicolors), 2)
        self.assertEqual(len(mc2.colors), 2)
        self.assertEqual(len(mc2.multicolors), 2)
        multicolors = [Multicolor(self.genome1, self.genome2, self.genome1, self.genome2),
                       Multicolor(self.genome4, self.genome3, self.genome4)]
        for mc in [mc1, mc2]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists as intersections, while the rest exists as set
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3, self.genome2, self.genome4,
                        self.genome3)
        guidance = [(self.genome1, self.genome5), (self.genome2, self.genome5), (self.genome4, self.genome3)]
        mc1, mc2, mc3 = Multicolor.split_colors(mc, guidance=guidance)
        multicolors = [Multicolor(self.genome1), Multicolor(self.genome4, self.genome3, self.genome4, self.genome3),
                       Multicolor(self.genome2, self.genome2)]
        for mc in [mc1, mc2, mc3]:
            self.assertTrue(mc in multicolors)
        # portion of a color exists as intersection, while the rest exists as subset
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3, self.genome2, self.genome4)
        guidance = [(self.genome1, self.genome5), (self.genome2, self.genome5),
                    (self.genome4, self.genome3, self.genome5)]
        mc1, mc2, mc3 = Multicolor.split_colors(mc, guidance=guidance)
        multicolors = [Multicolor(self.genome1), Multicolor(self.genome4, self.genome3, self.genome4),
                       Multicolor(self.genome2, self.genome2)]
        for mc in [mc1, mc2, mc3]:
            self.assertTrue(mc in multicolors)
        # both portions of color exist as intersections
        mc = Multicolor(self.genome1, self.genome2, self.genome4, self.genome3, self.genome1, self.genome2,
                        self.genome4, self.genome3)
        guidance = [(self.genome1, self.genome5), (self.genome2, self.genome5), (self.genome4, self.genome5),
                    (self.genome3, self.genome5)]
        mc1, mc2, mc3, mc4 = Multicolor.split_colors(mc, guidance=guidance)
        multicolors = [Multicolor(self.genome1, self.genome1), Multicolor(self.genome4, self.genome4),
                       Multicolor(self.genome2, self.genome2),
                       Multicolor(self.genome3, self.genome3)]
        for mc in [mc1, mc2, mc3, mc4]:
            self.assertTrue(mc in multicolors)
        # color does not exist in guidance
        mc = Multicolor(self.genome1, self.genome4, self.genome1, self.genome4)
        guidance = [(self.genome2, self.genome3), (self.genome2, ), (self.genome3, )]
        mc = Multicolor.split_colors(mc, guidance=guidance)[0]
        self.assertEqual(len(mc.colors), 2)
        self.assertEqual(len(mc.multicolors), 2)
        self.assertEqual(mc.multicolors[self.genome1], 2)
        self.assertEqual(mc.multicolors[self.genome4], 2)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()  # pragma: no cover
