# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

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

    def test_is_infinity_vertex(self):
        v1 = BGVertex("v1")
        i_v1 = BGVertex.construct_infinity_vertex_companion(v1)
        self.assertTrue(BGVertex.is_infinity_vertex(i_v1))
        self.assertFalse(BGVertex.is_infinity_vertex(v1))

    def test_json_identifier(self):
        # json identifier shall be unique per BGVertex and be of `int` type
        # json identifier is implemented as a property on BGVertex object
        # __hash__ is used
        v = BGVertex("name")
        json_id = v.json_id
        self.assertTrue(isinstance(json_id, int))
        self.assertEqual(json_id, hash(v))
        v.name = "name1"
        new_json_id = v.json_id
        self.assertTrue(isinstance(new_json_id, int))
        self.assertEqual(new_json_id, hash(v))
        self.assertNotEqual(json_id, new_json_id)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()         # pragma: no cover
