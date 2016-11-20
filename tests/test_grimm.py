from __future__ import unicode_literals

import io
import os
from collections import Counter

from bg.breakpoint_graph import BreakpointGraph
from bg.genome import BGGenome
from bg.grimm import GRIMMReader, GRIMMWriter
from bg.kbreak import KBreak
from bg.multicolor import Multicolor
from bg.vertices import TaggedBlockVertex, TaggedInfinityVertex

__author__ = 'Sergey Aganezov'
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest


class GRIMMReaderTestCase(unittest.TestCase):
    def test_is_genome_declaration_string(self):
        # string is named as genome declaration string if its first non empty element is ">"
        # genome name has to be specified after the ">" char, empty genome name is forbidden
        self.assertTrue(GRIMMReader.is_genome_declaration_string(">genome"))
        self.assertTrue(GRIMMReader.is_genome_declaration_string("    >genome"))
        self.assertTrue(GRIMMReader.is_genome_declaration_string("  \t  >genome"))
        self.assertTrue(GRIMMReader.is_genome_declaration_string(">genome   \t"))
        self.assertTrue(GRIMMReader.is_genome_declaration_string(">genome   "))
        self.assertTrue(GRIMMReader.is_genome_declaration_string("   >genome   "))
        self.assertFalse(GRIMMReader.is_genome_declaration_string("\tt   >genome"))
        self.assertFalse(GRIMMReader.is_genome_declaration_string("  t\t>genome"))
        self.assertFalse(GRIMMReader.is_genome_declaration_string("  t>genome"))
        self.assertFalse(GRIMMReader.is_genome_declaration_string("genome"))
        self.assertFalse(GRIMMReader.is_genome_declaration_string(">"))
        self.assertFalse(GRIMMReader.is_genome_declaration_string("     >   "))
        self.assertFalse(GRIMMReader.is_genome_declaration_string("     >"))
        self.assertFalse(GRIMMReader.is_genome_declaration_string(">   "))

    def test_parse_genome_declaration_string(self):
        # genome declaration string is parsed, by stripping the string from the right
        # and retrieving the string after the ">" character
        self.assertEqual(GRIMMReader.parse_genome_declaration_string(">genome"), BGGenome("genome"))
        self.assertEqual(GRIMMReader.parse_genome_declaration_string("  >genome  "), BGGenome("genome"))
        self.assertEqual(GRIMMReader.parse_genome_declaration_string(">genome__genome"), BGGenome("genome__genome"))
        self.assertEqual(GRIMMReader.parse_genome_declaration_string(">genome>genome"), BGGenome("genome>genome"))
        self.assertEqual(GRIMMReader.parse_genome_declaration_string(">genome.!/.#4"), BGGenome("genome.!/.#4"))

    def test_parse_data_string_error(self):
        # data string must contain a fragment termination symbol ($ or @)
        # and must contain space separated gene order information before fragment termination symbol
        data_string_1 = "   a b c d e    "
        data_string_2 = ""
        data_string_3 = " a -b -c d -e "
        data_string_4 = "$"
        data_string_5 = "@"
        data_string_6 = "@ a d s d"
        data_string_7 = "$a d s d"
        data_string_8 = "$-a d s d"
        data_string_9 = "@+a d s d"
        data_string_10 = "a b - -c d e $"
        for data_string in [data_string_1, data_string_2, data_string_3, data_string_4, data_string_5,
                            data_string_6, data_string_7, data_string_8, data_string_9, data_string_10]:
            with self.assertRaises(ValueError):
                GRIMMReader.parse_data_string(data_string)

    def test_parse_data_string_correct(self):
        # data string is parsed by getting information about genes order and individual orientations for each block (gene)
        # string based processing if performed
        # if no orientation is specified explicitly, positive orientation is assumed
        data_string = "a $"
        result = GRIMMReader.parse_data_string(data_string)
        self.assertEqual(result[0], "$")
        self.assertEqual(result[1][0][0], "+")
        self.assertEqual(result[1][0][1], "a")
        self.assertEqual(len(result[0]), 1)
        self.assertEqual(len(result[1]), 1)

        data_string = "a @"
        result = GRIMMReader.parse_data_string(data_string)
        self.assertEqual(result[0], "@")
        self.assertEqual(result[1][0][0], "+")
        self.assertEqual(result[1][0][1], "a")
        self.assertEqual(len(result[0]), 1)
        self.assertEqual(len(result[1]), 1)

        data_string = "     a -b c -d @ e f     "
        result = GRIMMReader.parse_data_string(data_string)
        self.assertEqual(result[0], "@")
        reference_genes = ["a", "b", "c", "d"]
        result_genes = [gene[1] for gene in result[1]]
        reference_signs = ["+", "-", "+", "-"]
        result_signs = [gene[0] for gene in result[1]]
        self.assertListEqual(result_genes, reference_genes)
        self.assertListEqual(result_signs, reference_signs)

        data_string = "     a -b +c -d $ e f     "
        result = GRIMMReader.parse_data_string(data_string)
        self.assertEqual(result[0], "$")
        reference_genes = ["a", "b", "c", "d"]
        result_genes = [gene[1] for gene in result[1]]
        reference_signs = ["+", "-", "+", "-"]
        result_signs = [gene[0] for gene in result[1]]
        self.assertListEqual(result_genes, reference_genes)
        self.assertListEqual(result_signs, reference_signs)

        data_string = "     a -b c -d @ e f $ g -h    "
        result = GRIMMReader.parse_data_string(data_string)
        self.assertEqual(result[0], "@")
        reference_genes = ["a", "b", "c", "d"]
        result_genes = [gene[1] for gene in result[1]]
        reference_signs = ["+", "-", "+", "-"]
        result_signs = [gene[0] for gene in result[1]]
        self.assertListEqual(result_genes, reference_genes)
        self.assertListEqual(result_signs, reference_signs)

    def test_get_list_of_edges_no_repeat_blocks(self):
        # depending on the fragment type adjacencies to be considered in BreakpointGraph are differ
        # in case of circular genome, additional adjacency is added between to outermost vertices
        # in case of linear genome, two extremity (infinity) vertices are appended to the start and end of the vertices list
        parsed_data = ("@", [("+", "a"), ("-", "b"), ("-", "a")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        reference = [(TaggedBlockVertex("at"), TaggedBlockVertex("at")),
                     (TaggedBlockVertex("ah"), TaggedBlockVertex("bh")),
                     (TaggedBlockVertex("bt"), TaggedBlockVertex("ah"))]
        self.assertDictEqual(Counter(result), Counter(reference))

        parsed_data = ("$", [("+", "a"), ("-", "b"), ("-", "a")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        reference = [(TaggedInfinityVertex("at"), TaggedBlockVertex("at")),
                     (TaggedBlockVertex("ah"), TaggedBlockVertex("bh")),
                     (TaggedBlockVertex("bt"), TaggedBlockVertex("ah")),
                     (TaggedBlockVertex("at"), TaggedInfinityVertex("at"))]
        self.assertDictEqual(Counter(result), Counter(reference))

        parsed_data = ("@", [("+", "a")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        reference = [(TaggedBlockVertex("ah"), TaggedBlockVertex("at"))]
        self.assertDictEqual(Counter(result), Counter(reference))

        parsed_data = ("$", [("-", "a"), ("-", "a")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        reference = [(TaggedInfinityVertex("ah"), TaggedBlockVertex("ah")),
                     (TaggedBlockVertex("at"), TaggedBlockVertex("ah")),
                     (TaggedBlockVertex("at"), TaggedInfinityVertex("at"))]
        self.assertDictEqual(Counter(result), Counter(reference))

    def test_get_list_of_edges_repeat_blocks_at_extremities(self):
        # if a fragment starts and / or ends with repeat block, that is denoted in a form of
        # repeat_block_name__repeat
        # IF this block is preserved as a block (i.e. located inside the fragment),
        # it will be transformed into a block "repeat_block_name" with
        #   an empty tag -- value "repeat" -- None
        # IF the block is not preserved (flanking repeat), it will be dismissed and its outermost extremity
        #   will be used to make its name (i.e. "repeat_block_name"h and it will be added as a tag to the infinity vertex
        #   created for a linear fragment
        # such information shall be recorded in respective infinity vertex, if a fragment is linear,
        # and in a normal tagged vertex, if fragment is circular

        # single repeat on the left extremity of linear fragment
        parsed_data = ("$", [("+", "a__repeat"), ("-", "b"), ("+", "c__tag:1")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        left_iv = TaggedInfinityVertex("bh")
        left_iv.add_tag("repeat", "ah")
        ch_vertex, ct_vertex = TaggedBlockVertex("ch"), TaggedBlockVertex("ct")
        ch_vertex.add_tag("tag", "1")
        ct_vertex.add_tag("tag", "1")
        reference = [(left_iv, TaggedBlockVertex("bh")),
                     (TaggedBlockVertex("bt"), ct_vertex),
                     (ch_vertex, TaggedInfinityVertex("ch"))]
        self.assertDictEqual(Counter(result), Counter(reference))

        # both extremities are "flanked" by repeats
        parsed_data = ("$", [("+", "a__repeat"), ("-", "b"), ("+", "c__tag:1:2"), ("-", "a__repeat")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        left_iv = TaggedInfinityVertex("bh")
        left_iv.add_tag("repeat", "ah")
        right_iv = TaggedInfinityVertex("ch")
        right_iv.add_tag("repeat", "ah")
        ch_vertex, ct_vertex = TaggedBlockVertex("ch"), TaggedBlockVertex("ct")
        ch_vertex.add_tag("tag", "1:2")
        ct_vertex.add_tag("tag", "1:2")
        reference = [(left_iv, TaggedBlockVertex("bh")),
                     (TaggedBlockVertex("bt"), ct_vertex),
                     (ch_vertex, right_iv)]
        self.assertDictEqual(Counter(result), Counter(reference))

        # fragment is specified as circular, all repeats shall be treated as normal blocks with half empty tags
        parsed_data = ("@", [("+", "a__repeat"), ("-", "b"), ("+", "c__tag:1"), ("-", "a__repeat")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        ch_vertex, ct_vertex = TaggedBlockVertex("ch"), TaggedBlockVertex("ct")
        ct_vertex.add_tag("tag", "1")
        ch_vertex.add_tag("tag", "1")
        ah_vertex, at_vertex = TaggedBlockVertex("ah"), TaggedBlockVertex("at")
        ah_vertex.add_tag("repeat", None)
        at_vertex.add_tag("repeat", None)
        reference = [(ah_vertex, TaggedBlockVertex("bh")),
                     (TaggedBlockVertex("bt"), ct_vertex),
                     (ch_vertex, ah_vertex),
                     (at_vertex, at_vertex)]
        self.assertDictEqual(Counter(result), Counter(reference))

    def test_is_comment_string(self):
        # a sting is considered a comment if it non empty first char is "#"
        self.assertTrue(GRIMMReader.is_comment_string("#"))
        self.assertTrue(GRIMMReader.is_comment_string("     #"))
        self.assertTrue(GRIMMReader.is_comment_string("#    "))
        self.assertTrue(GRIMMReader.is_comment_string("     #    "))
        self.assertTrue(GRIMMReader.is_comment_string("#  aaa  "))
        self.assertFalse(GRIMMReader.is_comment_string("a# "))
        self.assertTrue(GRIMMReader.is_comment_string("    ##  "))

    def test_is_comment_data_string(self):
        self.assertTrue(GRIMMReader.is_comment_data_string("# data :: "))
        self.assertTrue(GRIMMReader.is_comment_data_string("#data:: "))
        self.assertTrue(GRIMMReader.is_comment_data_string("   #data:: "))
        self.assertTrue(GRIMMReader.is_comment_data_string("   #data  :: "))
        self.assertTrue(GRIMMReader.is_comment_data_string("   #data  :: LALA"))
        self.assertTrue(GRIMMReader.is_comment_data_string("   #data  :: LALA : LULU"))
        self.assertTrue(GRIMMReader.is_comment_data_string("   #data  :: LALA : LULU=LILI"))

        self.assertFalse(GRIMMReader.is_comment_data_string("# data"))
        self.assertFalse(GRIMMReader.is_comment_data_string("# data:"))
        self.assertFalse(GRIMMReader.is_comment_data_string("# ldata:"))
        self.assertFalse(GRIMMReader.is_comment_data_string("# datal:"))

    def test_parse_comment_data_string_top_level(self):
        comment_data_string = "# data :: key=value"
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=comment_data_string)
        self.assertListEqual(path, [])
        self.assertEqual(key, "key")
        self.assertEqual(value, "value")
        comment_data_string = "#data::key = value"
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=comment_data_string)
        self.assertListEqual(path, [])
        self.assertEqual(key, "key")
        self.assertEqual(value, "value")

    def test_parse_comment_data_string_no_key(self):
        comment_data_string = "#data:: entry1 : entry2: = value"
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=comment_data_string)
        self.assertListEqual(path, ["entry1", "entry2"])
        self.assertEqual(key, "")
        self.assertEqual(value, "value")
        comment_data_string = "#data:: = value"
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=comment_data_string)
        self.assertListEqual(path, [])
        self.assertEqual(key, "")
        self.assertEqual(value, "value")

    def test_parse_comment_data_string_no_value(self):
        comment_data_string = "#data:: entry1 : entry2: key = "
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=comment_data_string)
        self.assertListEqual(path, ["entry1", "entry2"])
        self.assertEqual(key, "key")
        self.assertEqual(value, "")
        comment_data_string = "#data:: key = "
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=comment_data_string)
        self.assertListEqual(path, [])
        self.assertEqual(key, "key")
        self.assertEqual(value, "")

    def test_parse_comment_data_string_no_key_value(self):
        comment_data_string = "#data:: "
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=comment_data_string)
        self.assertListEqual(path, [])
        self.assertEqual(key, "")
        self.assertEqual(value, "")
        comment_data_string = "#data:: = "
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=comment_data_string)
        self.assertListEqual(path, [])
        self.assertEqual(key, "")
        self.assertEqual(value, "")

    def test_parse_comment_data_string(self):
        data_string = "# data :: fragment : name = scaffold1"
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=data_string)
        self.assertEqual(path, ["fragment"])
        self.assertEqual(key, "name")
        self.assertEqual(value, "scaffold1")
        data_string = "# data :: fragment : origin: name = ALLPATHS-LG"
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=data_string)
        self.assertEqual(path, ["fragment", "origin"])
        self.assertEqual(key, "name")
        self.assertEqual(value, "ALLPATHS-LG")
        data_string = "# data :: genome : origin: name = ALLPATHS-LG"
        path, (key, value) = GRIMMReader.parse_comment_data_string(comment_data_string=data_string)
        self.assertEqual(path, ["genome", "origin"])
        self.assertEqual(key, "name")
        self.assertEqual(value, "ALLPATHS-LG")

    def test_get_breakpoint_from_file(self):
        # full workflow testing with dummy data
        # correct cases are assumed with all kind of crazy indentation and rubbish data mixed in, but still correct
        data = ["",
                "\t",
                "#comment1",
                ">genome_name_1",
                "      #comment1",
                "a b $",
                "\tc -a @\t",
                "   #comment1   ",
                "\t>genome_name_2",
                "a $",
                "",
                "\n\t"]
        file_like = io.StringIO("\n".join(data))
        result_bg = GRIMMReader.get_breakpoint_graph(file_like)
        self.assertTrue(isinstance(result_bg, BreakpointGraph))
        self.assertEqual(len(list(result_bg.connected_components_subgraphs())), 3)
        self.assertEqual(len(list(result_bg.edges())), 6)
        self.assertEqual(len(list(result_bg.nodes())), 9)
        multicolors = [Multicolor(BGGenome("genome_name_1"), BGGenome("genome_name_2")),
                       Multicolor(BGGenome("genome_name_1")),
                       Multicolor(BGGenome("genome_name_2"))]
        for bgedge in result_bg.edges():
            self.assertTrue(bgedge.multicolor in multicolors)
        infinity_edges = [bgedge for bgedge in result_bg.edges() if bgedge.is_infinity_edge]
        self.assertEqual(len(infinity_edges), 3)

        data = [">genome_1",
                "a $",
                ">genome_2",
                "a b $",
                "# this is a bad genome",
                ">genome_3",
                "a b c $",
                ">genome_4",
                "   # chromosome 1",
                "b c $",
                ">genome_5",
                "c $"]
        file_like = io.StringIO("\n".join(data))
        result_bg = GRIMMReader.get_breakpoint_graph(file_like)
        self.assertTrue(isinstance(result_bg, BreakpointGraph))
        self.assertEqual(len(list(result_bg.connected_components_subgraphs())), 4)
        self.assertEqual(len(list(result_bg.edges())), 8)
        self.assertEqual(len(list(result_bg.nodes())), 12)
        genome1, genome2, genome3 = BGGenome("genome_1"), BGGenome("genome_2"), BGGenome("genome_3")
        genome4, genome5 = BGGenome("genome_4"), BGGenome("genome_5")
        multicolors = [Multicolor(genome1, genome2, genome3),
                       Multicolor(genome1),
                       Multicolor(genome2, genome3),
                       Multicolor(genome2),
                       Multicolor(genome3, genome4),
                       Multicolor(genome3, genome4, genome5),
                       Multicolor(genome4),
                       Multicolor(genome5)]
        for bgedge in result_bg.edges():
            self.assertTrue(bgedge.multicolor in multicolors)
        infinity_edges = [bgedge for bgedge in result_bg.edges() if bgedge.is_infinity_edge]
        self.assertEqual(len(infinity_edges), 6)
        infinity_multicolors = [multicolor for multicolor in multicolors if len(multicolor.multicolors) != 2]
        for bgedge in infinity_edges:
            self.assertTrue(bgedge.multicolor in infinity_multicolors)

    def test_get_breakpoint_from_file_with_comment_data_string(self):
        data = ["",
                "\t",
                "#comment1",
                ">genome_name_1",
                "      #comment1",
                "# data :: fragment : name = chromosome_X",
                "a b $",
                "   #comment1   ",
                "\t>genome_name_2",
                "#data::fragment:name=scaffold111",
                "a $",
                "",
                "\n\t"]
        file_like = io.StringIO("\n".join(data))
        result_bg = GRIMMReader.get_breakpoint_graph(file_like, merge_edges=False)
        self.assertTrue(isinstance(result_bg, BreakpointGraph))
        self.assertEqual(len(list(result_bg.connected_components_subgraphs())), 3)
        self.assertEqual(len(list(result_bg.edges())), 5)
        self.assertEqual(len(list(result_bg.nodes())), 7)
        multicolors = [Multicolor(BGGenome("genome_name_1")),
                       Multicolor(BGGenome("genome_name_2"))]
        condensed_multicolors = [Multicolor(BGGenome("genome_name_1")),
                                 Multicolor(BGGenome("genome_name_2")),
                                 Multicolor(BGGenome("genome_name_1"), BGGenome("genome_name_2"))]
        for bgedge in result_bg.edges():
            self.assertTrue(bgedge.multicolor in multicolors)
        for bgedge in result_bg.edges():
            condensed_edge = result_bg.get_condensed_edge(vertex1=bgedge.vertex1, vertex2=bgedge.vertex2)
            self.assertTrue(condensed_edge.multicolor in condensed_multicolors)
        infinity_edges = [bgedge for bgedge in result_bg.edges() if bgedge.is_infinity_edge]
        self.assertEqual(len(infinity_edges), 4)
        for bgedge in result_bg.edges():
            data = bgedge.data
            self.assertIn("fragment", data)
            self.assertIsInstance(data["fragment"], dict)
            self.assertIn("name", data["fragment"])
            self.assertIn(data["fragment"]["name"], {"chromosome_X", "scaffold111"})
        ah = result_bg.get_vertex_by_name("ah")
        bt = result_bg.get_vertex_by_name("bt")
        ahi = result_bg.get_vertex_by_name("ah__infinity")
        edge = result_bg.get_edge_by_two_vertices(vertex1=ah, vertex2=bt)
        self.assertTupleEqual(edge.data["fragment"]["forward_orientation"], (ah, bt))
        iedge = result_bg.get_edge_by_two_vertices(vertex1=ah, vertex2=ahi)
        self.assertTupleEqual(iedge.data["fragment"]["forward_orientation"], (ah, ahi))


class GRIMMWriterTestCase(unittest.TestCase):
    def setUp(self):
        self.genome1 = BGGenome("red")
        self.genome2 = BGGenome("green")
        self.genome3 = BGGenome("blue")
        self.single_genome_bg = BreakpointGraph()
        self.two_genome_bg = BreakpointGraph()
        self.four_genome_bg = BreakpointGraph()

    @staticmethod
    def _populate_bg(data, merge_edges=False):
        file_like = io.StringIO("\n".join(data))
        bg = GRIMMReader.get_breakpoint_graph(file_like, merge_edges=merge_edges)
        return bg

    def _get_mouse_data(self):
        return [
            ">Mouse",
            "1 2 3 4 $",
            "5 6 7 8 $"
        ]

    def _get_human_data(self):
        return [
            ">Human",
            "1 4 3 2 $",
            "5 -7 -6 8 $"
        ]

    def _get_rat_data(self):
        return [
            ">Rat",
            "0 1 4 5 $",
            "10 12 8 7 $"
        ]

    def _get_chimp_data(self):
        return [
            ">Chimpanzee",
            "5 6 7 8 $",
            "1 -4 -3 -2 $"
        ]

    def _populate_single_genome_bg(self, merge_edges=False):
        data = self._get_mouse_data()
        bg = self._populate_bg(data=data, merge_edges=merge_edges)
        self.single_genome_bg = bg

    def _populate_two_genomes_bg(self, merge_edges=False):
        data = self._get_human_data() + self._get_mouse_data()
        bg = self._populate_bg(data=data, merge_edges=merge_edges)
        self.two_genome_bg = bg

    def _populate_four_genomes_bg(self, merge_edges=False):
        data = self._get_human_data() + self._get_mouse_data() + self._get_chimp_data() + self._get_rat_data()
        bg = self._populate_bg(data=data, merge_edges=merge_edges)
        self.four_genome_bg = bg

    def test_get_grimm_strings_from_breakpoint_graph_single_genome(self):
        self._populate_single_genome_bg()
        grimm_strings = GRIMMWriter.get_blocks_in_grimm_from_breakpoint_graph(bg=self.single_genome_bg)
        self.assertEqual(len(grimm_strings), 3)
        self.assertIn(">Mouse", grimm_strings)
        possibilities_1 = ["1 2 3 4 $", "-4 -3 -2 -1 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_1)))
        possibilities_2 = ["5 6 7 8 $", "-8 -7 -6 -5 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_2)))

    def test_get_grimm_strings_from_breakpoints_graph_two_genomes(self):
        self._populate_two_genomes_bg()
        grimm_strings = GRIMMWriter.get_blocks_in_grimm_from_breakpoint_graph(bg=self.two_genome_bg)
        self.assertEqual(len(grimm_strings), 6)
        self.assertIn(">Mouse", grimm_strings)
        self.assertIn(">Human", grimm_strings)

        possibilities_1 = ["1 2 3 4 $", "-4 -3 -2 -1 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_1)))
        possibilities_2 = ["5 6 7 8 $", "-8 -7 -6 -5 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_2)))

        possibilities_3 = ["1 4 3 2 $", "-2 -3 -4 -1 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_3)))
        possibilities_4 = ["5 -7 -6 8 $", "-8 6 7 -5 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_4)))

    def test_get_grimm_from_breakpoint_graph_four_genomes(self):
        self._populate_four_genomes_bg()
        grimm_strings = GRIMMWriter.get_blocks_in_grimm_from_breakpoint_graph(bg=self.four_genome_bg)

        self.assertEqual(len(grimm_strings), 12)
        self.assertIn(">Mouse", grimm_strings)
        self.assertIn(">Human", grimm_strings)
        self.assertIn(">Rat", grimm_strings)
        self.assertIn(">Chimpanzee", grimm_strings)

        possibilities_1 = ["1 2 3 4 $", "-4 -3 -2 -1 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_1)))
        possibilities_2 = ["5 6 7 8 $", "-8 -7 -6 -5 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_2)))

        possibilities_3 = ["1 4 3 2 $", "-2 -3 -4 -1 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_3)))
        possibilities_4 = ["5 -7 -6 8 $", "-8 6 7 -5 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_4)))

        possibilities_5 = ["0 1 4 5 $", "-5 -4 -1 -0 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_5)))
        possibilities_6 = ["10 12 8 7 $", "-7 -8 -12 -10 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_6)))

        possibilities_7 = ["5 6 7 8 $", "-8 -7 -6 -5 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_7)))
        possibilities_8 = ["1 -4 -3 -2 $", "2 3 4 -1 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_8)))

    def test_get_grimm_from_breakpoint_graph_single_chromosome(self):
        data = [
            ">Mouse",
            "1 2 3 4 5 $"
        ]
        bg = self._populate_bg(data=data)
        grimm_strings = GRIMMWriter.get_blocks_in_grimm_from_breakpoint_graph(bg=bg)
        self.assertEqual(len(grimm_strings), 2)
        self.assertIn(">Mouse", grimm_strings)
        possibilities_1 = ["1 2 3 4 5 $", "-5 -4 -3 -2 -1 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_1)))

    def test_output_genomes_as_grimm(self):
        self._populate_four_genomes_bg(merge_edges=True)
        file_name = "file_name.txt"
        GRIMMWriter.print_genomes_as_grimm_blocks_orders(bg=self.four_genome_bg,
                                                         file_name=file_name)
        try:
            with open(file_name, "rt") as source:
                new_bg = GRIMMReader.get_breakpoint_graph(stream=source,
                                                          merge_edges=True)
                self.assertEqual(len(list(new_bg.nodes())), len(list(self.four_genome_bg.nodes())))
                self.assertEqual(len(list(new_bg.edges())), len(list(self.four_genome_bg.edges())))

                self.assertSetEqual(set(new_bg.nodes()), set(self.four_genome_bg.nodes()))
                self.assertSetEqual(new_bg.get_overall_set_of_colors(),
                                    self.four_genome_bg.get_overall_set_of_colors())

        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def test_get_fragments_grimm_from_breakpoint_graph_single_genome(self):
        data = [
            ">Mouse",
            "# data :: fragment : name = scaffold1",
            "1 repeat__LC-1 $",
            "# data :: fragment : name = scaffold2",
            "2 $",
            "# data :: fragment : name = scaffold3",
            "repeat__ALC 3 $"
        ]
        bg = self._populate_bg(data=data)
        grimm_strings = GRIMMWriter.get_fragments_in_grimm_from_breakpoint_graph(bg=bg)
        possibilities_1 = ["scaffold1 $", "-scaffold1 $"]
        possibilities_2 = ["scaffold2 $", "-scaffold2 $"]
        possibilities_3 = ["scaffold3 $", "-scaffold3 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_1)))
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_2)))
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_3)))

    def test_get_fragments_grimm_from_breakpoint_graph_single_genome_with_merges(self):
        data = [
            ">Mouse",
            "# data :: fragment : name = scaffold1",
            "1 $",
            "# data :: fragment : name = scaffold2",
            "2 $",
            "# data :: fragment : name = scaffold3",
            "repeat__ALC 3 $"
        ]
        bg = self._populate_bg(data=data)
        iv1 = bg.get_vertex_by_name("1h__infinity")
        iv2 = bg.get_vertex_by_name("2h__infinity")
        v1 = bg.get_vertex_by_name("1h")
        v2 = bg.get_vertex_by_name("2h")
        kbreak = KBreak(start_edges=[(v1, iv1), (v2, iv2)],
                        result_edges=[(v1, v2), (iv1, iv2)],
                        multicolor=Multicolor(BGGenome("Mouse")))
        bg.apply_kbreak(kbreak=kbreak)
        grimm_strings = GRIMMWriter.get_fragments_in_grimm_from_breakpoint_graph(bg=bg)
        possibilities_1 = ["scaffold1 -scaffold2 $", "scaffold2 -scaffold1 $"]
        possibilities_3 = ["scaffold3 $", "-scaffold3 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_1)))
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_3)))

    def test_get_fragments_grimm_from_breakpoint_graph_single_genome_with_repeat_based_merges(self):
        data = [
            ">Mouse",
            "# data :: fragment : name = scaffold1",
            "1 ALC__repeat $",
            "# data :: fragment : name = scaffold2",
            "ALC__repeat 2 $",
            "# data :: fragment : name = scaffold3",
            "ALC__repeat 3 $"
        ]
        bg = self._populate_bg(data=data)
        iv1 = bg.get_vertex_by_name("1h__repeat:ALCt__infinity")
        iv2 = bg.get_vertex_by_name("2t__repeat:ALCh__infinity")
        v1 = bg.get_vertex_by_name("1h")
        v2 = bg.get_vertex_by_name("2t")
        kbreak = KBreak(start_edges=[(v1, iv1), (v2, iv2)],
                        result_edges=[(v1, v2), (iv1, iv2)],
                        multicolor=Multicolor(BGGenome("Mouse")))
        bg.apply_kbreak(kbreak=kbreak)
        grimm_strings = GRIMMWriter.get_fragments_in_grimm_from_breakpoint_graph(bg=bg)
        possibilities_1 = ["scaffold1 scaffold2 $", "-scaffold2 -scaffold1 $"]
        possibilities_3 = ["scaffold3 $", "-scaffold3 $"]
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_1)))
        self.assertTrue(any(map(lambda entry: entry in grimm_strings, possibilities_3)))


if __name__ == '__main__':
    unittest.main()
