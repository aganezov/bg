# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "devel"

import unittest
from bg.vertices import BGVertex_JSON_SCHEMA_JSON_KEY, BGVertex, BlockVertex, InfinityVertex


class BGVertexTestCase(unittest.TestCase):
    def setUp(self):
        """ Heavily utilized values in multiple test """
        self.str_name1 = "name1"
        self.str_name2 = "name2"
        self.str_name3 = "name3"
        self.str_name4 = "name4"
        self.str_name5 = "name5"
        self.int_name1 = 1
        self.int_name2 = 2
        self.int_name3 = 3
        self.vertex_class = BGVertex

    def test_empty_initialization(self):
        with self.assertRaises(TypeError):
            self.vertex_class()

    def test_initialization(self):
        v = self.vertex_class(self.str_name1)
        self.assertEqual(v.name, self.str_name1)

    def test__hash__(self):
        """ hash value from BGVertex is defines as hash value from the name of respective vertex """
        self.assertEqual(hash(self.vertex_class(self.str_name1)), hash(self.vertex_class(self.str_name1).name))

    def test__eq__(self):
        """ BGVertices are equal is they are of the same class and have equal hash values """
        v1 = self.vertex_class(self.str_name1)
        v2 = self.vertex_class(self.str_name1)
        v3 = self.vertex_class(self.str_name3)
        self.assertEqual(v1, v2)
        self.assertNotEqual(v1, v3)
        self.assertNotEqual(v2, v3)
        for non_bg_vertex_value in [1, "1", (1,), [1]]:
            self.assertNotEqual(v1, non_bg_vertex_value)

    def test_is_something_vertex_request_stopper(self):
        """ BGVertex serves as a "stopper" class for all lookups like is_.+_vertex and returns False to all of them
            Examples:
                vertex.is_regular_vertex
                vertex.is_infinity_vertex
                vertex.is_block_vertex
        """
        for vertex_type_string in ["lala1", "lala2", "lala2", "lala4", "etc"]:
            # dummy values have no meaning, so inherited test cases can recall this test method
            vertex_request_type = "is_" + vertex_type_string + "_vertex"
            self.assertFalse(getattr(self.vertex_class(self.str_name1), vertex_request_type))

    def test_json_identifier(self):
        # json identifier shall be unique per BGVertex and be of `int` type
        # json identifier is implemented as a property on BGVertex object
        # __hash__ is used
        v = self.vertex_class(self.str_name1)
        json_id = v.json_id
        self.assertTrue(isinstance(json_id, int))
        self.assertEqual(json_id, hash(v))
        v.name = self.int_name2
        new_json_id = v.json_id
        self.assertTrue(isinstance(new_json_id, int))
        self.assertEqual(new_json_id, hash(v))
        self.assertNotEqual(json_id, new_json_id)

    def test_json_serialization(self):
        # a BGVertex class instance shall be serializable into the JSON based object
        # such serialization shall contain all breakpoint graph relative information about the vertex
        # as well as a special json_id field that unique identifies this instance of BGVertex
        v = self.vertex_class(self.str_name1)
        ref_result = {
            "name": self.str_name1,
            'v_id': v.json_id
        }
        result = v.to_json(schema_info=False)
        self.assertDictEqual(ref_result, result)
        # with json_schema_key
        ref_result[BGVertex_JSON_SCHEMA_JSON_KEY] = v.json_schema_name
        result = v.to_json(schema_info=True)
        self.assertDictEqual(ref_result, result)
        # a non-string name attribute value shall be translated into a string object
        v = self.vertex_class(self.int_name1)
        ref_result = {
            "name": "1",
            'v_id': v.json_id
        }
        result = v.to_json(schema_info=False)
        self.assertDictEqual(ref_result, result)

    def test_json_deserialization_correct_default_schema(self):
        # a BGVertex class instance is to be read from the JSON based object data
        # not all JSON object attributes are to be stored in BGVertex object
        json_object = {
            "name": self.str_name1,
            "_py__bg_vertex_json_schema": self.vertex_class.json_schema_name,
            "json_id": 1
        }
        vertex = self.vertex_class.from_json(json_object)
        self.assertTrue(isinstance(vertex, self.vertex_class))
        # explicitly specified json schema to work with
        # but since nothing is passed into in "schema" argument to the from_json function
        # default to the BGVertex.json_schema is performed
        json_schema_name = self.vertex_class(self.str_name1).json_schema_name
        json_object = {
            BGVertex_JSON_SCHEMA_JSON_KEY: json_schema_name,
            "name": self.str_name1,
            "json_id": 1
        }
        vertex = self.vertex_class.from_json(json_object)
        self.assertTrue(isinstance(vertex, self.vertex_class))
        self.assertEqual(vertex.name, self.str_name1)
        # there must be a "name" field in json object to be serialized
        with self.assertRaises(ValueError):
            json_object = {"json_id": 1}
            self.vertex_class.from_json(json_object)

    def test_get_vertex_class_from_vertex_name(self):
        # correct versions
        # as different types of vertices have different repr names,
        # they shall be ambiguously identified by their string name
        block_vertex_class = BlockVertex
        infinity_vertex_class = InfinityVertex
        bv = BlockVertex(self.str_name1)
        iv = InfinityVertex(self.str_name1)
        self.assertEqual(BGVertex.get_vertex_class_from_vertex_name(bv.name), block_vertex_class)
        self.assertEqual(BGVertex.get_vertex_class_from_vertex_name(iv.name), infinity_vertex_class)

    def test_get_vertex_name_root(self):
        # strips all suffixes from the string name and returns the root of it
        # most vertices, except for a BlockVertex will have single of multiple suffixes to it
        #   Example:
        #       InfinityVertex("lala").name == lala__infinity
        # "__" serves as name_separator, and is inherited from BGVertex. Everything before the first __ is considered
        # vertex name root
        string = "aaa"
        self.assertEqual(BGVertex.get_vertex_name_root(string), "aaa")
        string = ""
        self.assertEqual(BGVertex.get_vertex_name_root(string), "")
        string = "aaa" + BGVertex.NAME_SEPARATOR + ""
        self.assertEqual(BGVertex.get_vertex_name_root(string), "aaa")
        string = "aaa" + BGVertex.NAME_SEPARATOR + "aaa" + BGVertex.NAME_SEPARATOR + "aaa"
        self.assertEqual(BGVertex.get_vertex_name_root(string), "aaa")


class BlockVertexTestCase(BGVertexTestCase):
    """ Update vertex_class to call BlockVertex rather than BGVertex, and update overwritten portions of the class """
    def setUp(self):
        super().setUp()
        self.vertex_class = BlockVertex

    def test_inheritance(self):
        self.assertIsInstance(self.vertex_class(self.str_name1), BGVertex)

    def test_is_block_vertex(self):
        # BlockVertex defines two properties
        #   * is_regular_vertex, which is a broad class of vertices, that correspond to ends of fully present genomic blocks
        #   * is_block_vertex, which is a narrower class of vertices, that correspond to ends of gene/synteny blocks
        v = self.vertex_class(self.str_name1)
        self.assertTrue(v.is_regular_vertex)
        self.assertTrue(v.is_block_vertex)


class InfinityVertexTestCase(BGVertexTestCase):
    """ Update vertex_class to call InfinityVertex rather than BGVertex, and update overwritten portions of the class """
    def setUp(self):
        super().setUp()
        self.vertex_class = InfinityVertex
        self.block_vertex = BlockVertex(self.str_name1)

    def test_initialization(self):
        #
        # InfinityVertex overwrites the access to the "name" attribute, thus keeping internal representation as is,
        # while returning on call a calculated on the fly value, that has InfinityVertex name suffix in it
        i_v = InfinityVertex(self.block_vertex.name)
        ref_name = InfinityVertex.NAME_SEPARATOR.join([self.block_vertex.name, InfinityVertex.NAME_SUFFIX])
        self.assertEqual(i_v.name, ref_name)

    def test_is_irregular_vertex(self):
        # InfinityVertex defines two properties
        #   * is_irregular_vertex, which is a broad class of vertices, that correspond to ends of genomic fragments
        #   * is_infinity__vertex, which is a narrower class of vertices, that correspond to traditional extrimities of genomic fragments
        i_v = InfinityVertex(self.block_vertex)
        self.assertTrue(i_v.is_infinity_vertex)
        self.assertTrue(i_v.is_irregular_vertex)

    def test_inheritance(self):
        self.assertIsInstance(InfinityVertex(self.block_vertex), BGVertex)

    def test_json_identifier(self):
        # json identifier shall be unique per BGVertex and be of `int` type
        # json identifier is implemented as a property on BGVertex object
        # __hash__ is used
        v = self.vertex_class(self.block_vertex)
        json_id = v.json_id
        self.assertTrue(isinstance(json_id, int))
        self.assertEqual(json_id, hash(v))
        v.name = self.int_name2
        new_json_id = v.json_id
        self.assertTrue(isinstance(new_json_id, int))
        self.assertEqual(new_json_id, hash(v))
        self.assertNotEqual(json_id, new_json_id)

    def test_json_serialization(self):
        # a InfinityVertex class instance shall be serializable into the JSON based object
        # such serialization shall contain all breakpoint graph relative information about the vertex
        # as well as a special json_id field that unique identifies this instance of BGVertex
        v = self.vertex_class(self.block_vertex.name)
        ref_result = {
            "name": InfinityVertex.NAME_SEPARATOR.join([self.str_name1, InfinityVertex.NAME_SUFFIX]),
            'v_id': v.json_id
        }
        result = v.to_json(schema_info=False)
        self.assertDictEqual(ref_result, result)
        # with json_schema_key
        ref_result[BGVertex_JSON_SCHEMA_JSON_KEY] = v.json_schema_name
        result = v.to_json(schema_info=True)
        self.assertDictEqual(ref_result, result)
        # a non-string name attribute value shall be translated into a string object
        v = self.vertex_class(BlockVertex(1).name)
        ref_result = {
            "name": InfinityVertex.NAME_SEPARATOR.join(["1", InfinityVertex.NAME_SUFFIX]),
            'v_id': v.json_id
        }
        result = v.to_json(schema_info=False)
        self.assertDictEqual(ref_result, result)

    def test_json_deserialization_correct_default_schema(self):
        # a BGVertex class instance is to be read from the JSON based object data
        # not all JSON object attributes are to be stored in BGVertex object
        json_object = {
            "name": self.str_name1,
            "json_id": 1
        }
        vertex = self.vertex_class.from_json(json_object)
        self.assertTrue(isinstance(vertex, self.vertex_class))
        # explicitly specified json schema to work with
        # but since nothing is passed into in "schema" argument to the from_json function
        # default to the BGVertex.json_schema is performed
        json_schema_name = self.vertex_class(self.block_vertex).json_schema_name
        json_object = {
            BGVertex_JSON_SCHEMA_JSON_KEY: json_schema_name,
            "name": self.str_name1,
            "json_id": 1
        }
        vertex = self.vertex_class.from_json(json_object)
        self.assertTrue(isinstance(vertex, self.vertex_class))
        self.assertEqual(vertex.name, InfinityVertex.NAME_SEPARATOR.join([self.str_name1, InfinityVertex.NAME_SUFFIX]))
        # there must be a "name" field in json object to be serialized
        with self.assertRaises(ValueError):
            json_object = {"json_id": 1}
            self.vertex_class.from_json(json_object)

if __name__ == '__main__':  # pragma: no cover
    unittest.main()         # pragma: no cover
