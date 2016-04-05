import unittest

from bg.distances import scj
from tests.test_grimm import GRIMMWriterTestCase


class SCJTestCase(unittest.TestCase):
    def test_circular_genomes_case_1(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 @",
            "# data :: fragment : name=scaffold2",
            "4 5 6 @"
        ]
        g2_data = [
            ">B",
            "1 3 -2 @",
            "6 5 4 @"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 12)

    def test_circular_genomes_case_2(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 @",
            "# data :: fragment : name=scaffold2",
            "4 5 6 @"
        ]
        g2_data = [
            ">B",
            "1 2 -3 @",
            "-4 5 6 @"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 8)

    def test_circular_genomes_case_3(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 @",
            "# data :: fragment : name=scaffold2",
            "4 5 6 @"
        ]
        g2_data = [
            ">B",
            "1 2 3 @",
            "4 5 6 @"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 0)

    def test_circular_genomes_case_4(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 4 5 6 @"
        ]
        g2_data = [
            ">B",
            "1 @",
            "2 @",
            "3 @",
            "4 @",
            "5 @",
            "6 @"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 12)

    def test_linear_genomes_case_1(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 $",
            "# data :: fragment : name=scaffold2",
            "4 5 6 $"
        ]
        g2_data = [
            ">B",
            "1 2 3 $",
            "4 5 6 $"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 0)

    def test_linear_genomes_case_2(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 $",
            "# data :: fragment : name=scaffold2",
            "4 5 6 $"
        ]
        g2_data = [
            ">B",
            "1 2 3 4 5 6 $"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 1)

    def test_linear_genomes_case_3(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 4 5 6 $",
        ]
        g2_data = [
            ">B",
            "1 $",
            "2 $",
            "3 $",
            "4 $",
            "5 $",
            "6 $"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 5)

    def test_linear_genomes_case_4(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 4 5 6 $",
        ]
        g2_data = [
            ">B",
            "1 $",
            "-6 -5 -4 -3 -2 $"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 1)

    def test_linear_genomes_case_5(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 4 5 6 $",
        ]
        g2_data = [
            ">B",
            "-3 -2 -1 $",
            "-6 -5 -4 $"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 1)

    def test_linear_genomes_case_6(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 4 5 6 $",
        ]
        g2_data = [
            ">B",
            "-3 -2 -1 -6 -5 -4 $"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 2)

    def test_mixed_genomes_case_1(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 4 5 $",
            "6 @"
        ]
        g2_data = [
            ">B",
            "-3 -2 -1 @",
            "-6 -5 -4 $"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 4)

    def test_mixed_genomes_case_2(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 4 5 6 ALC__repeat$"
        ]
        g2_data = [
            ">B",
            "1 2 3 4 5 6 @"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 1)

    def test_mixed_genomes_case_3(self):
        g1_data = [
            ">A",
            "# data :: fragment : name=scaffold1",
            "1 2 3 4 5 6 $"
        ]
        g2_data = [
            ">B",
            "1 3 2 4 5 6 $"
        ]
        bg = GRIMMWriterTestCase._populate_bg(data=g1_data + g2_data)
        self.assertEqual(scj(bg), 6)

if __name__ == '__main__':
    unittest.main()
