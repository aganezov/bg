from bg.io import GRIMMReader

__author__ = 'Sergey Aganezov'
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

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
        for data_string in [data_string_1, data_string_2, data_string_3, data_string_4, data_string_5,
                            data_string_6, data_string_7, data_string_8, data_string_9]:
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
        referece_signs = ["+", "-", "+", "-"]
        result_signs = [gene[0] for gene in result[1]]
        self.assertListEqual(result_genes, reference_genes)
        self.assertListEqual(result_signs, referece_signs)

        data_string = "     a -b c -d $ e f     "
        result = GRIMMReader.parse_data_string(data_string)
        self.assertEqual(result[0], "$")
        reference_genes = ["a", "b", "c", "d"]
        result_genes = [gene[1] for gene in result[1]]
        referece_signs = ["+", "-", "+", "-"]
        result_signs = [gene[0] for gene in result[1]]
        self.assertListEqual(result_genes, reference_genes)
        self.assertListEqual(result_signs, referece_signs)

        data_string = "     a -b c -d @ e f $ g -h    "
        result = GRIMMReader.parse_data_string(data_string)
        self.assertEqual(result[0], "@")
        reference_genes = ["a", "b", "c", "d"]
        result_genes = [gene[1] for gene in result[1]]
        referece_signs = ["+", "-", "+", "-"]
        result_signs = [gene[0] for gene in result[1]]
        self.assertListEqual(result_genes, reference_genes)
        self.assertListEqual(result_signs, referece_signs)

if __name__ == '__main__':
    unittest.main()
