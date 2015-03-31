# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.vertex import BGVertex, BGVertex_JSON_SCHEMA_JSON_KEY


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

    def test_json_serialization(self):
        # a BGVertex class instance shall be serializable into the JSON based object
        # such serialization shall contain all breakpoint graph relative information about the vertex
        # as well as a special json_id field that unique identifies this instance of BGVertex
        v = BGVertex("name")
        ref_result = {
            "name": "name",
            'v_id': v.json_id
        }
        result = v.to_json(schema_info=False)
        self.assertDictEqual(ref_result, result)
        self.assertTrue(isinstance(result["v_id"], int))
        # with json_schema_key
        ref_result = {
            BGVertex_JSON_SCHEMA_JSON_KEY: v.json_schema_name,
            "name": "name",
            'v_id': v.json_id
        }
        result = v.to_json(schema_info=True)
        self.assertDictEqual(ref_result, result)
        self.assertTrue(isinstance(result["v_id"], int))
        # no a string name attribute value shall be translated into a string object
        v = BGVertex(1)
        ref_result = {
            "name": "1",
            'v_id': v.json_id
        }
        result = v.to_json(schema_info=False)
        self.assertDictEqual(ref_result, result)
        self.assertTrue(isinstance(result["v_id"], int))

    def test_json_deserialization_correct_default_schema(self):
        # a BGVertex class instance is to be read from the JSON based object data
        # not all JSON object attributes are to be stored in BGVertex object
        json_object = {
            "name": "vertex_name",
            "json_id": 1
        }
        vertex = BGVertex.from_json(json_object)
        self.assertTrue(isinstance(vertex, BGVertex))
        # explicitly specified json schema to work with
        # but since nothing is passed into in "schema" argument to the from_json function
        # default to the BGVertex.json_schema is performed
        json_schema_name = BGVertex("v").json_schema_name
        json_object = {
            BGVertex_JSON_SCHEMA_JSON_KEY: json_schema_name,
            "name": "vertex_name",
            "json_id": 1
        }
        vertex = BGVertex.from_json(json_object)
        self.assertTrue(isinstance(vertex, BGVertex))
        self.assertEqual(vertex.name, "vertex_name")
        # there must be a "name" field in json object to be serialized
        with self.assertRaises(KeyError):
            json_object = {"json_id": 1}
            BGVertex.from_json(json_object)

    def test_json_deserialization_supplied_schema(self):
        # if the scheme is supplied as a "json_scheme_class" , it shall be applied to the object
        # the _py__bg_vertex_json_schema shall be ignored at the BGVertex.from_json method level
        json_object = {
            BGVertex_JSON_SCHEMA_JSON_KEY: BGVertex.json_schema_name,
            "name": 1,
            "json_id": 1
        }

        class DefaultEnsureNameStringJSONSchema(BGVertex.BGVertexJSONSchema):
            def make_object(self, data):
                return BGVertex(str(data.get("name", "default_name")))

        vertex = BGVertex.from_json(json_object, json_schema_class=DefaultEnsureNameStringJSONSchema)
        self.assertTrue(isinstance(vertex.name, str))
        self.assertEqual(vertex.name, "1")

        json_object = {
            BGVertex_JSON_SCHEMA_JSON_KEY: BGVertex.json_schema_name,
            "json_id": 1
        }
        vertex = BGVertex.from_json(json_object, json_schema_class=DefaultEnsureNameStringJSONSchema)
        self.assertTrue(isinstance(vertex.name, str))
        self.assertEqual(vertex.name, "default_name")

if __name__ == '__main__':  # pragma: no cover
    unittest.main()         # pragma: no cover
