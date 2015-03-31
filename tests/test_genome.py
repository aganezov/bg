__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.genome import BGGenome


class BGGenomeTestCase(unittest.TestCase):
    def test_initialization_incorrect(self):
        with self.assertRaises(TypeError):
            g = BGGenome()

    def test_initialization(self):
        g = BGGenome("name")
        self.assertEqual(g.name, "name")

    def test_hash(self):
        g = BGGenome("name")
        self.assertEqual(hash(g), hash("name"))

    def test_json_id(self):
        g = BGGenome("name")
        json_id = g.json_id
        self.assertEqual(json_id, hash(g.name))
        self.assertTrue(isinstance(json_id, int))
        g.name = "name1"
        new_json_id = g.json_id
        self.assertEqual(new_json_id, hash(g.name))
        self.assertTrue(isinstance(json_id, int))
        self.assertNotEqual(json_id, new_json_id)

    def test__eq__(self):
        g1 = BGGenome("name1")
        g2 = BGGenome("name2")
        self.assertNotEqual(g1, g2)
        g2.name = "name1"
        self.assertEqual(g1, g2)
        self.assertNotEqual(g1, 5)
        self.assertNotEqual(g1, "name1")
        self.assertNotEqual(g1, [g1])


if __name__ == '__main__':
    unittest.main()
