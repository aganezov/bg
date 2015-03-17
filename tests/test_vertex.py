# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.vertex import BGVertex


class BGVertexTestCase(unittest.TestCase):
    def test_empty_initialization(self):
        with self.assertRaises(TypeError):
            BGVertex()

    def test_name_initialization(self):
        v = BGVertex("name")
        self.assertEqual(v.name, "name")
        self.assertDictEqual({}, v.info)

    def test_full_initialization(self):
        info = {"red": 1, "blue": 2}
        v = BGVertex("name", info=info)
        self.assertEqual(v.name, "name")
        self.assertDictEqual(v.info, info)

    def test__hash__(self):
        name = "name"
        v = BGVertex(name)
        self.assertEqual(hash(name), hash(v))
        name = 1
        v = BGVertex(name)
        self.assertEqual(hash(name), hash(v))

    def test_equality(self):
        name1 = "name1"
        v1 = BGVertex(name1)
        name2 = "name1"
        v2 = BGVertex(name2)
        self.assertEqual(v1, v2)
        name3 = "name3"
        v3 = BGVertex(name3)
        self.assertNotEqual(v1, v3)
        self.assertNotEqual(v2, v3)
        self.assertNotEqual(v1, 5)

    def test_construct_infinity_vertex(self):
        with self.assertRaises(TypeError):
            BGVertex.construct_infinity_vertex_companion()
        string_vertex = "vertex"
        result = BGVertex.construct_infinity_vertex_companion(string_vertex)
        self.assertTrue(isinstance(result, str))
        self.assertEqual(result, "vertex__infinity")
        bgvertex = BGVertex("vertex")
        result = BGVertex.construct_infinity_vertex_companion(bgvertex)
        self.assertTrue(isinstance(result, BGVertex))
        self.assertEqual(result, BGVertex("vertex__infinity"))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()         # pragma: no cover
