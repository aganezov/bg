# -*- coding: utf-8 -*-
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest

from bg.genome import BGGenome
from bg.multicolor import Multicolor


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
        ###############################################################################################
        #
        # cases when Multicolor object is compared with a non-Multicolor object
        # this equality comparison is always False
        #
        ###############################################################################################
        for non_multicolor_type_object in [1, (1,), [1], "1", Mock()]:
            self.assertNotEqual(Multicolor(), non_multicolor_type_object)

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
        ###############################################################################################
        #
        # Multicolor object is never greater or equal to the non-Multicolor object
        #
        ###############################################################################################
        for non_multicolor_object in [1, (1,), [1,], "1", Mock()]:
            self.assertFalse(mc1 >= non_multicolor_object)
            self.assertFalse(mc1 > non_multicolor_object)

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

    ###############################################################################################
    #
    # following tests are aimed at generic splitting based on provided set of good colors
    # it is compatible with tree consistent multicolor splitting, but is not limited to it
    #
    ###############################################################################################

    def test_split_colors_account_for_multiplicity_in_guidance(self):
        ###############################################################################################
        #
        # when no guidance is specified, a multicolor shall be split according to its own colors
        # when `account_for_multiplicity_in_guidance` is specified
        #   each color in the splitted result shall have multiplicity as it had in the targeted multicolor
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome1, self.genome2, self.genome3, self.genome3, self.genome3)
        ref = [Multicolor(self.genome1, self.genome1),
               Multicolor(self.genome2),
               Multicolor(self.genome3, self.genome3, self.genome3)]
        result = Multicolor.split_colors(mc, account_for_color_multiplicity_in_guidance=True)
        self.assertEqual(len(result), 3)
        for result_mc in result:
            self.assertIn(result_mc, ref)
        ###############################################################################################
        ###############################################################################################
        #
        # a simple guidance with a single multicolor, that has only a single color with multiplicity one
        #
        ###############################################################################################
        mc = Multicolor(self.genome1)
        guidance = [Multicolor(self.genome1)]
        result = Multicolor.split_colors(mc, guidance=guidance, account_for_color_multiplicity_in_guidance=True)
        self.assertEqual(len(result), 1)
        mc = result[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        ###############################################################################################
        ###############################################################################################
        #
        # color exists in guidance only as subset, then it shall be retrieved fully on its own
        #
        ###############################################################################################
        mc = Multicolor(self.genome1)
        guidance = [Multicolor(self.genome1, self.genome4)]
        result = Multicolor.split_colors(mc, guidance=guidance, account_for_color_multiplicity_in_guidance=True)
        self.assertEqual(len(result), 1)
        mc = result[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        ###############################################################################################
        ###############################################################################################
        #
        # color exists in guidance both as subset and a set itself, and thus shall be retrieved fully
        #
        ###############################################################################################
        mc = Multicolor(self.genome1)
        guidance = [Multicolor(self.genome1), Multicolor(self.genome1, self.genome4), Multicolor(self.genome4)]
        result = Multicolor.split_colors(mc, guidance=guidance, account_for_color_multiplicity_in_guidance=True)
        self.assertEqual(len(result), 1)
        mc = result[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        ###############################################################################################
        ###############################################################################################
        #
        # color does not exist in guidance, and shall be retrieved fully, as an appendix
        #
        ###############################################################################################
        mc = Multicolor(self.genome1)
        guidance = [Multicolor(self.genome2, self.genome4)]
        result = Multicolor.split_colors(mc, guidance=guidance, account_for_color_multiplicity_in_guidance=True)
        self.assertEqual(len(result), 1)
        mc = result[0]
        self.assertEqual(len(mc.colors), 1)
        self.assertEqual(len(mc.multicolors), 1)
        self.assertEqual(mc.multicolors[self.genome1], 1)
        ###############################################################################################
        ###############################################################################################
        #
        # some color in guidance present twice in the splitting multicolor
        # and thus shall be retrieved fully twice
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome1, self.genome1, self.genome2, self.genome2)
        guidance = [Multicolor(self.genome1, self.genome2)]
        ref1 = guidance[0]
        ref2 = Multicolor(self.genome1)
        result = Multicolor.split_colors(mc, guidance=guidance, account_for_color_multiplicity_in_guidance=True)
        self.assertEqual(len(result), 3)
        for result_mc in result:
            self.assertIn(result_mc, [ref1, ref2])
        ###############################################################################################
        ###############################################################################################
        #
        # some colors in guidance have non empty intersections (with multiplicity > 1) with s splitting color
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome1, self.genome2, self.genome2)
        guidance = [Multicolor(self.genome1, self.genome2, self.genome3)]
        ref = Multicolor(self.genome1, self.genome2)
        result = Multicolor.split_colors(mc, guidance=guidance, account_for_color_multiplicity_in_guidance=True)
        self.assertEqual(len(result), 2)
        for result_mc in result:
            self.assertEqual(result_mc, ref)
        ###############################################################################################
        ###############################################################################################
        #
        # some color in guidance is present twice in the splitting color
        # some color in guidance has a non empty intersection with splitting color
        #   that interferes with multicolor in guidance, that is fully present
        # full presence must overtake in this case
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome1, self.genome2, self.genome2)
        guidance = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome1, self.genome2, self.genome3)]
        ref = Multicolor(self.genome1, self.genome2)
        result = Multicolor.split_colors(mc, guidance=guidance,
                                         account_for_color_multiplicity_in_guidance=True)
        self.assertEqual(len(result), 2)
        for result_mc in result:
            self.assertEqual(result_mc, ref)
        ###############################################################################################
        ###############################################################################################
        #
        # both fully present and non-empty intersection colors are present in guidance
        # the most complex test case
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome1, self.genome2, self.genome2, self.genome3)
        guidance = [Multicolor(self.genome1, self.genome2, self.genome3),
                    Multicolor(self.genome1, self.genome1, self.genome2, self.genome2)]
        ref1 = Multicolor(self.genome1, self.genome1, self.genome2, self.genome2)
        ref2 = Multicolor(self.genome3)
        result = Multicolor.split_colors(mc, guidance=guidance,
                                         account_for_color_multiplicity_in_guidance=True)
        self.assertEqual(len(result), 2)
        for result_mc in result:
            self.assertIn(result_mc, [ref1, ref2])

    def test_split_colors_do_not_account_for_multiplicity_in_guidance(self):
        ###############################################################################################
        ###############################################################################################
        #
        # no guidance, targeted multicolor shall be split on separate colors
        # keeping respective colors multiplicity intact in each splitted peace
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome1, self.genome2, self.genome3, self.genome3, self.genome3)
        result = Multicolor.split_colors(mc, account_for_color_multiplicity_in_guidance=False)
        ref = [Multicolor(self.genome1, self.genome1),
               Multicolor(self.genome2),
               Multicolor(self.genome3, self.genome3, self.genome3)]
        self.assertEqual(len(result), 3)
        for result_mc in result:
            self.assertIn(result_mc, ref)
        ###############################################################################################
        ###############################################################################################
        #
        # simple case, where guidance contains already multicolor with multiplicity 1
        # targeted multicolor shall be split based on those colors
        #     but multiplicity of respective colors in the result shall be kept as it was in the targetted multicolor
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome1, self.genome2, self.genome3, self.genome3, self.genome3)
        guidance = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome3)]
        result = Multicolor.split_colors(mc, guidance=guidance, account_for_color_multiplicity_in_guidance=False)
        ref = [Multicolor(self.genome1, self.genome1, self.genome2),
               Multicolor(self.genome3, self.genome3, self.genome3)]
        self.assertEqual(len(result), 2)
        for result_mc in result:
            self.assertIn(result_mc, ref)
        ###############################################################################################
        ###############################################################################################
        #
        # more complex case, when guidance contains multicolor with multiplicity of colors bigger than 1
        # in this case, those guidance multicolors will be simplified to same colors multicolors
        #   but multiplicity of respective colors will be changed to 1
        # resulted multicolor split shall contain multiplicity of respective colors, as in the original one
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome1, self.genome2, self.genome3, self.genome3, self.genome3)
        guidance = [Multicolor(self.genome1, self.genome2, self.genome1), Multicolor(self.genome3, self.genome3)]
        result = Multicolor.split_colors(mc, guidance=guidance, account_for_color_multiplicity_in_guidance=False)
        ref = [Multicolor(self.genome1, self.genome1, self.genome2),
               Multicolor(self.genome3, self.genome3, self.genome3)]
        self.assertEqual(len(result), 2)
        for result_mc in result:
            self.assertIn(result_mc, ref)
        ###############################################################################################
        ###############################################################################################
        #
        # case when guidance has multiple multicolors, that after simplification would look the same
        #   (they differ only in the multiplicity of respective colors)
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome2, self.genome3, self.genome3, self.genome4, self.genome4)
        guidance = [Multicolor(self.genome1), Multicolor(self.genome1, self.genome1), Multicolor(self.genome1, self.genome1),
                    Multicolor(self.genome2, self.genome3),
                    Multicolor(self.genome4)]
        result = Multicolor.split_colors(mc, guidance=guidance, account_for_color_multiplicity_in_guidance=False)
        ref = [Multicolor(self.genome1),
               Multicolor(self.genome2, self.genome3, self.genome3),
               Multicolor(self.genome4, self.genome4)]
        self.assertEqual(len(result), 3)
        for result_mc in result:
            self.assertIn(result_mc, ref)

    def test_color_splits_no_guidance_sorting(self):
        ###############################################################################################
        #
        # order of multicolors in guidance affects the splitting
        # if two colors in guidance are both present in the splitting multicolor
        #   then the first multicolor in the guidance  will be retrieved, but the second might not be,
        #   as not enough information will be left in the splitting multicolor
        #
        ###############################################################################################
        ###############################################################################################
        #
        # simple case, when there are two multicolors in the guidance
        # we don't account for the
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome2, self.genome3)
        guidance = [Multicolor(self.genome1, self.genome2),
                    Multicolor(self.genome1, self.genome2, self.genome3)]
        result = Multicolor.split_colors(mc, guidance=guidance, sorted_guidance=True)
        self.assertEqual(len(result), 2)
        ref = [Multicolor(self.genome1, self.genome2), Multicolor(self.genome3)]
        for result_mc in result:
            self.assertIn(result_mc, ref)
        ###############################################################################################
        ###############################################################################################
        #
        # simple case, when there are two multicolors in the guidance
        # we don't account for the
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome1, self.genome2, self.genome3, self.genome3, self.genome3)
        guidance = [Multicolor(self.genome1),
                    Multicolor(self.genome1, self.genome2),
                    Multicolor(self.genome3, self.genome3, self.genome3, self.genome2)]
        result = Multicolor.split_colors(mc, guidance=guidance, sorted_guidance=True)
        ref = [Multicolor(self.genome1), Multicolor(self.genome2, self.genome3, self.genome3, self.genome3)]
        self.assertEqual(len(result), 3)
        for result_mc in result:
            self.assertIn(result_mc, ref)

    def test_split_colors_with_empty_multicolor_in_guidance(self):
        ###############################################################################################
        #
        # empty multicolor in splitting guidance shall not have any affect on the splitting procedure
        #
        ###############################################################################################
        mc = Multicolor(self.genome1, self.genome2)
        guidance = [Multicolor(self.genome1), Multicolor()]
        result = Multicolor.split_colors(mc, guidance=guidance)
        self.assertEqual(len(result), 2)
        ref = [Multicolor(self.genome1), Multicolor(self.genome2)]
        for result_mc in result:
            self.assertIn(result_mc, ref)

    ###############################################################################################
    #
    # end of splitting test cases
    #
    ###############################################################################################

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

    def test_intersect(self):
        # intersection of two multicolors shall be considered in the same fashion, as intersection of sets
        # with a note, that multiplicity if shared colors shall be represented in the result
        mc1 = Multicolor(self.genome1, self.genome2, self.genome3)
        mc2 = Multicolor(self.genome1, self.genome2)
        mc3 = mc1.intersect(mc2)
        self.assertEqual(len(mc3.colors), 2)
        self.assertEqual(mc3.multicolors[self.genome1], 1)
        self.assertEqual(mc3.multicolors[self.genome2], 1)
        self.assertEqual(mc1.intersect(mc2), mc2.intersect(mc1))
        ###############################################################################################
        mc1 = Multicolor(self.genome1, self.genome1, self.genome2, self.genome3)
        mc2 = Multicolor(self.genome2, self.genome2, self.genome1, self.genome3)
        mc3 = mc1.intersect(mc2)
        self.assertEqual(len(mc2.colors), 3)
        self.assertEqual(mc3.multicolors[self.genome1], 1)  # second multicolor has only one copy of this color
        self.assertEqual(mc3.multicolors[self.genome2], 1)  # first multicolor has only one copy of this color
        self.assertEqual(mc1.intersect(mc2), mc2.intersect(mc1))
        ###############################################################################################
        mc1 = Multicolor(self.genome1, self.genome2, self.genome2, self.genome2)
        mc2 = Multicolor(self.genome2, self.genome2, self.genome2)
        mc3 = mc1.intersect(mc2)
        self.assertEqual(len(mc3.colors), 1)
        self.assertEqual(mc3.multicolors[self.genome2], 3)
        self.assertEqual(mc1.intersect(mc2), mc2.intersect(mc1))

    def test_intersect_incorrect_type(self):
        for incorrect_argument in [1, (1,), [1], "1", Mock()]:
            with self.assertRaises(TypeError):
                Multicolor().intersect(incorrect_argument)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()  # pragma: no cover
