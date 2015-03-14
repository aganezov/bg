from collections import Counter
import io
from bg import BreakpointGraph, Multicolor
from bg.bg_io import GRIMMReader

__author__ = 'Sergey Aganezov'
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest


class GRIMMReaderTestCase(unittest.TestCase):
    def test_is_genome_declaration_string(self):
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
        self.assertEqual(GRIMMReader.parse_genome_declaration_string(">genome"), "genome")
        self.assertEqual(GRIMMReader.parse_genome_declaration_string("  >genome  "), "genome")
        self.assertEqual(GRIMMReader.parse_genome_declaration_string(">genome__genome"), "genome__genome")
        self.assertEqual(GRIMMReader.parse_genome_declaration_string(">genome>genome"), "genome>genome")
        self.assertEqual(GRIMMReader.parse_genome_declaration_string(">genome.!/.#4"), "genome.!/.#4")

    def test_parse_data_string_error(self):
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

        data_string = "     a -b c -d $ e f     "
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

    def test_get_list_of_edges(self):
        parsed_data = ("@", [("+", "a"), ("-", "b"), ("-", "a")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        reference = [("at", "at"), ("ah", "bh"), ("bt", "ah")]
        self.assertDictEqual(Counter(result), Counter(reference))

        parsed_data = ("$", [("+", "a"), ("-", "b"), ("-", "a")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        reference = [("at__infinity", "at"), ("ah", "bh"), ("bt", "ah"), ("at", "at__infinity")]
        self.assertDictEqual(Counter(result), Counter(reference))

        parsed_data = ("@", [("+", "a")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        reference = [("ah", "at")]
        self.assertDictEqual(Counter(result), Counter(reference))

        parsed_data = ("$", [("-", "a"), ("-", "a")])
        result = GRIMMReader.get_edges_from_parsed_data(parsed_data)
        reference = [("ah__infinity", "ah"), ("at", "ah"), ("at", "at__infinity")]
        self.assertDictEqual(Counter(result), Counter(reference))

    def test_is_comment_string(self):
        self.assertTrue(GRIMMReader.is_comment_string("#"))
        self.assertTrue(GRIMMReader.is_comment_string("     #"))
        self.assertTrue(GRIMMReader.is_comment_string("#    "))
        self.assertTrue(GRIMMReader.is_comment_string("     #    "))
        self.assertTrue(GRIMMReader.is_comment_string("#  aaa  "))
        self.assertFalse(GRIMMReader.is_comment_string("a# "))
        self.assertTrue(GRIMMReader.is_comment_string("    ##  "))

    def test_get_breakpoint_from_file(self):
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
        multicolors = [Multicolor("genome_name_1", "genome_name_2"),
                       Multicolor("genome_name_1"),
                       Multicolor("genome_name_2")]
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
        multicolors = [Multicolor("genome_1", "genome_2", "genome_3"),
                       Multicolor("genome_1"),
                       Multicolor("genome_2", "genome_3"),
                       Multicolor("genome_2"),
                       Multicolor("genome_3", "genome_4"),
                       Multicolor("genome_3", "genome_4", "genome_5"),
                       Multicolor("genome_4"),
                       Multicolor("genome_5")]
        for bgedge in result_bg.edges():
            self.assertTrue(bgedge.multicolor in multicolors)
        infinity_edges = [bgedge for bgedge in result_bg.edges() if bgedge.is_infinity_edge]
        self.assertEqual(len(infinity_edges), 6)
        infinity_multicolors = [multicolor for multicolor in multicolors if len(multicolor.multicolors) != 2]
        for bgedge in infinity_edges:
            self.assertTrue(bgedge.multicolor in infinity_multicolors)

if __name__ == '__main__':
    unittest.main()
