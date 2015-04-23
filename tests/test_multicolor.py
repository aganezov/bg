# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.multicolor import Multicolor
from bg.genome import BGGenome


class MulticolorTestCase(unittest.TestCase):
    # in comments bellow "genome" and "color" represent the same concept
    # if not specified otherwise explicitly

    def setUp(self):
        # some heavily used variables
        self.genome1 = BGGenome("red")
        self.genome2 = BGGenome("green")
        self.genome3 = BGGenome("blue")
        self.genome4 = BGGenome("black")
        self.genome5 = BGGenome("yellow")

    def test_empty_initialization(self):
        # empty multicolor shall be initialisable but contain no information about the colors or their multiplicity
        mc = Multicolor()
        self.assertEqual(len(mc.colors), 0)
        self.assertEqual(len(mc.multicolors), 0)

    def test_single_initialization(self):
        # simple case initialization where only one genome with multiplicity one is supplied
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
        # cases when multiple genomes with different multiplicities (from 1 to >1 are specified)
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
        # multicolors are called equal
        # if they contain information about hte same colors with same multiplicity for each color
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
        # multicolor can be updated by multiple arguments
        # they shall add information about colors (if color was not present before) and/or their multiplicity
        # change is inplace
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
        # multicolors can be merged
        # left_merge adds information about colors and their multiplicity from right specified genome, to the left one
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
        # multicolors can be merged into a new multicolor
        # "merge" method creates a new multicolor with information from a variable number of provided multicolors
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
        # multicolor supports removing information about colors, taking into account to their multiplicity
        # multicolor support deletion using information from Multicolor instance or any iterable
        # negative counts for the color multiplicity are not supported:
        #   so if color had multiplicity 1 and this color was supposed to be deleted twice, it will be just deleted
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
        # - operator os overloaded to provide "delete" alike behaviour, but with a creation of a new Multicolor instance
        # only Multicolor instance is supported as an argument
        # for any other argument type a TypeError is raised
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
        # -= operator is overloaded and support only Multicolor instance as an argument
        # for any other argument a TypeError is raised
        # behalves just like the "delete" method
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
        # + operator is overloaded and works just like a "merge" method, but support only Multicolor instance as an argument
        # for any other type of argument a TypeError is raised
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

    def test__iadd__(self):
        # += operator is overloaded and works just like a "left_merge" method
        # but supports only a Multicolor instance as an argument
        # for any other type of argument a TypeError is raised
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
        # multicolor are compared as follows:
        # for all the colors in the left argument of comparison, checks that multiplicity of that color in right argument is
        # less (less-equal)
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
        # multicolor are compared as follows:
        # for all the colors in the left argument of comparison, checks that multiplicity of that color in right argument is
        # greater (greater-equal)
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
        # similarity score for multicolors is computed as follows:
        # for every mutual color, the smallest multiplicity of such color in two Multicolors is considered
        # similarity score is computed as the sum over such min multiplicities of all shared colors
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
        # TODO: fix with a tree consistent multicolors tests
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
        # TODO: fix with a tree consistent multicolors tests
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
        # TODO: fix with tree consistent multicolors tests
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
        # TODO: fix with tree consistent multicolors tests
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

    def test_hashable_representation(self):
        # every multicolor has to have a hashable representation, that can be utilized in a set/dict
        # for a fast check against multicolor instance
        ################################################
        # the idea is to use sorted Counter.elements() method and convert into sorted tuple on the fly
        genome_list = [self.genome1, self.genome2, self.genome3, self.genome4, self.genome1, self.genome2, self.genome1]
        mc = Multicolor(*genome_list)
        ref_tuple = tuple(sorted(genome_list))
        result = mc.hashable_representation
        self.assertTrue(isinstance(result, tuple))
        self.assertTupleEqual(result, ref_tuple)
        mc1 = Multicolor(*result)
        self.assertEqual(mc, mc1)
        # non-equal multicolors shall have different hashable representations
        mc1 = Multicolor(*genome_list[:-2])
        mc2 = Multicolor(*genome_list[:-1])
        self.assertNotEqual(mc1, mc2)
        self.assertNotEqual(mc1.hashable_representation, mc2.hashable_representation)
        # there shall be no errors or exceptions raised while taking hash of hashable_representation
        result = mc.hashable_representation
        self.assertEqual(hash(result), hash(ref_tuple))

    def test__mull__(self):
        # empty multicolor shall be kept as is regardless of multiplier
        mc = Multicolor()
        for multiplier in range(10):
            self.assertEqual(mc * multiplier, Multicolor())
        # multiplying by 0 shall make any multicolor an empty one
        mc1 = Multicolor(self.genome1)
        self.assertEqual(mc1 * 0, Multicolor())
        mc2 = Multicolor(self.genome1, self.genome2, self.genome3)
        self.assertEqual(mc2 * 0, Multicolor())
        mc3 = Multicolor(self.genome1, self.genome2, self.genome1)
        self.assertEqual(mc3 * 0, Multicolor())
        # multiplying by an integer shall multiply each color multiplicity respectively
        mc = Multicolor(self.genome1, self.genome2, self.genome3, self.genome1, self.genome2, self.genome1)
        for multiplier in range(1, 50):
            ref_multicolor = Multicolor()
            for _ in range(multiplier):
                ref_multicolor += mc
            self.assertEqual(mc * multiplier, ref_multicolor)

    def test__mull__incorrect(self):
        # multiplication only by integer value is allowed
        mc = Multicolor()
        for incorrect_multiplier in [.1, (1,), [1], "1"]:
            with self.assertRaises(TypeError):
                mc = mc * incorrect_multiplier


if __name__ == '__main__':  # pragma: no cover
    unittest.main()  # pragma: no cover
