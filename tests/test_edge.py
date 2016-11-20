# -*- coding: utf-8 -*-
from collections import Counter

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from bg.genome import BGGenome
from bg.multicolor import Multicolor
from bg.utils import dicts_are_equal
from bg.vertices import BlockVertex, InfinityVertex, TaggedBlockVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest
from bg.edge import BGEdge, BGEdge_JSON_SCHEMA_JSON_KEY


class BGEdgeTestCase(unittest.TestCase):
    def setUp(self):
        # heavily utilized variables
        self.genome1 = BGGenome("red")
        self.genome2 = BGGenome("green")
        self.genome3 = BGGenome("blue")
        self.genome4 = BGGenome("black")
        self.genome4 = BGGenome("yellow")

    def test_empty_initialization_incorrect(self):
        with self.assertRaises(TypeError):
            # a BGEdge wrapper is meant to wrap something, but not nothing
            BGEdge()

    def test_initialization(self):
        # simple correct initialization of BGEdge instance
        v1 = BlockVertex("v1")
        v2 = BlockVertex("v2")
        multicolor = Multicolor(self.genome3)
        edge = BGEdge(vertex1=v1,
                      vertex2=v2,
                      multicolor=multicolor)
        self.assertEqual(edge.vertex1, v1)
        self.assertEqual(edge.vertex2, v2)
        self.assertEqual(edge.multicolor, multicolor)

    def test_merging_correct(self):
        # two BGEdges can be merged together into a third, separate BGEdge
        # that would contain information from both supplied BGEdges in terms of colors and multiplicities
        # such merge is allowed only if a pair of vertices in both BGEdges is the same
        # ordering of vertices if not a concern, since edges in BreakpointGraph are not directed
        v1 = BlockVertex("v1")
        v2 = BlockVertex("v2")
        multicolor = Multicolor(self.genome3)
        multicolor1 = Multicolor(self.genome2)
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        edge2 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor1)
        merged_edge = BGEdge.merge(edge1, edge2)
        self.assertEqual(merged_edge.vertex1, v1)
        self.assertEqual(merged_edge.vertex2, v2)
        self.assertEqual(merged_edge.multicolor, multicolor + multicolor1)

    def test_merging_incorrect(self):
        # cases when vertices in two supplied for the merging edges are not consistent
        v1 = BlockVertex("v1")
        v2 = BlockVertex("v2")
        v3 = BlockVertex("v3")
        v4 = BlockVertex("v4")
        multicolor = Multicolor(self.genome3)
        multicolor1 = Multicolor(self.genome2)
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        edge2 = BGEdge(vertex1=v1, vertex2=v3, multicolor=multicolor1)
        with self.assertRaises(ValueError):
            BGEdge.merge(edge1, edge2)
        edge2 = BGEdge(vertex1=v3, vertex2=v2, multicolor=multicolor1)
        with self.assertRaises(ValueError):
            BGEdge.merge(edge1, edge2)
        edge2 = BGEdge(vertex1=v3, vertex2=v4, multicolor=multicolor1)
        with self.assertRaises(ValueError):
            BGEdge.merge(edge1, edge2)
        edge2 = BGEdge(vertex1=v1, vertex2=v1, multicolor=multicolor1)
        with self.assertRaises(ValueError):
            BGEdge.merge(edge1, edge2)
        edge2 = BGEdge(vertex1=v2, vertex2=v2, multicolor=multicolor1)
        with self.assertRaises(ValueError):
            BGEdge.merge(edge1, edge2)
        edge2 = BGEdge(vertex1=v3, vertex2=v1, multicolor=multicolor1)
        with self.assertRaises(ValueError):
            BGEdge.merge(edge1, edge2)

    def test_equality(self):
        # edges are called equal if they connect same pairs of vertices and have same multicolor assigned to them
        v1 = BlockVertex("v1")
        v2 = BlockVertex("v2")
        v3 = BlockVertex("v3")
        v4 = BlockVertex("v4")
        multicolor = Multicolor(self.genome3)
        multicolor1 = Multicolor(self.genome2)
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        edge2 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor1)
        edge3 = BGEdge(vertex1=v1, vertex2=v3, multicolor=multicolor1)
        edge4 = BGEdge(vertex1=v3, vertex2=v4, multicolor=multicolor)
        self.assertNotEqual(edge1, edge2)
        self.assertNotEqual(edge1, edge3)
        self.assertNotEqual(edge2, edge3)
        self.assertNotEqual(edge1, edge4)
        edge4 = BGEdge(vertex1=v2, vertex2=v1, multicolor=multicolor)
        edge5 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        self.assertEqual(edge1, edge4)
        self.assertEqual(edge1, edge5)
        self.assertEqual(edge4, edge5)
        self.assertNotEqual(edge1, 5)
        edge6 = BGEdge(vertex1=v3, vertex2=v1, multicolor=multicolor)
        self.assertNotEqual(edge1, edge6)

        self.assertEqual(edge1, edge4)
        edge4.data = {"fragment": {"name": 1}}
        edge1.data = {"fragment": {"name": 2}}
        self.assertNotEqual(edge1, edge4)
        edge1.data = {"fragment": {"name": 1}}
        self.assertEqual(edge1, edge4)

    def test_is_infinity_edge(self):
        # and edge is called an infinity edge if at least one of its vertices is an infinity vertex
        v1 = BlockVertex("v1")
        v2 = BlockVertex("v2")
        v3 = InfinityVertex("v3")
        multicolor = Multicolor(self.genome3)
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        edge2 = BGEdge(vertex1=v1, vertex2=v3, multicolor=multicolor)
        edge3 = BGEdge(vertex1=v3, vertex2=v1, multicolor=multicolor)
        edge4 = BGEdge(vertex1=v3, vertex2=v3, multicolor=multicolor)
        self.assertFalse(edge1.is_infinity_edge)
        self.assertTrue(edge2.is_infinity_edge)
        self.assertTrue(edge3.is_infinity_edge)
        self.assertTrue(edge4.is_infinity_edge)

    def test_is_irregular_edge(self):
        # and edge is called an irregular edge if at least one of its vertices is an irregular vertex
        v1 = BlockVertex("v1")
        v2 = BlockVertex("v2")
        v3 = InfinityVertex("v3")
        multicolor = Multicolor(self.genome3)
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        edge2 = BGEdge(vertex1=v1, vertex2=v3, multicolor=multicolor)
        edge3 = BGEdge(vertex1=v3, vertex2=v1, multicolor=multicolor)
        edge4 = BGEdge(vertex1=v3, vertex2=v3, multicolor=multicolor)
        self.assertFalse(edge1.is_irregular_edge)
        self.assertTrue(edge2.is_irregular_edge)
        self.assertTrue(edge3.is_irregular_edge)
        self.assertTrue(edge4.is_irregular_edge)

    def test_iter_over_colors_json_ids(self):
        # when multiedge is serialized into json a list of colors in it referenced by their ids
        # the multiplicity of colors has to be preserved
        v1 = BlockVertex("v1")
        v2 = BlockVertex("v2")
        genomes = [self.genome1, self.genome1, self.genome2, self.genome3, self.genome2]
        multicolor = Multicolor(*genomes)
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        json_ids = bgedge.colors_json_ids
        self.assertTrue(isinstance(json_ids, list))
        json_ids_list = json_ids
        self.assertEqual(len(json_ids_list), 5)
        ref_json_ids = Counter(genome.json_id for genome in genomes)
        res_json_ids = Counter(json_ids_list)
        self.assertDictEqual(ref_json_ids, res_json_ids)
        # case when color objects are not a BGGenome, but some other hashable object without json_id attribute
        v1 = BlockVertex("v1")
        v2 = BlockVertex("v2")
        colors = ["red", "red", "green", "black", "yellow", "green"]
        multicolor = Multicolor(*colors)
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        json_ids = bgedge.colors_json_ids
        self.assertTrue(isinstance(json_ids, list))
        json_ids_list = json_ids
        self.assertEqual(len(json_ids_list), 6)
        ref_json_ids = Counter(hash(genome) for genome in colors)
        res_json_ids = Counter(json_ids_list)
        self.assertDictEqual(ref_json_ids, res_json_ids)
        # case when color objects are mixed objects: BGGenome objects, just hashable, have json_id but not BGGenome
        v1 = BlockVertex("v1")
        v2 = BlockVertex("v2")
        mock1, mock2 = Mock(), Mock()
        mock1.json_id = 5
        mock2.json_id = 6
        colors = [self.genome1, mock1, self.genome2, "black", mock2, self.genome2]
        multicolor = Multicolor(*colors)
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        json_ids = bgedge.colors_json_ids
        self.assertTrue(isinstance(json_ids, list))
        json_ids_list = list(json_ids)
        self.assertEqual(len(json_ids_list), 6)
        ref_json_ids = Counter(genome.json_id if hasattr(genome, "json_id") else hash(genome) for genome in colors)
        res_json_ids = Counter(json_ids_list)
        self.assertDictEqual(ref_json_ids, res_json_ids)

    def test_json_serialization(self):
        # simple case of serialization, single color, no multiplicity
        v1, v2 = BlockVertex("v1"), BlockVertex("v2")
        color1 = BGGenome("genome1")
        multicolor = Multicolor(color1)
        edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        ref_result = {
            "vertex1_id": v1.json_id,
            "vertex2_id": v2.json_id,
            "multicolor": [color1.json_id]
        }
        self.assertDictEqual(edge.to_json(schema_info=False), ref_result)
        # case where multiple colors are present, multiplicity is 1 for every of them
        color2 = BGGenome("genome2")
        multicolor = Multicolor(color1, color2)
        edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        result = edge.to_json()
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(result["vertex1_id"], v1.json_id)
        self.assertEqual(result["vertex2_id"], v2.json_id)
        self.assertSetEqual(set(result["multicolor"]), {color1.json_id, color2.json_id})
        self.assertEqual(result[BGEdge_JSON_SCHEMA_JSON_KEY], edge.json_schema_name)
        # case where multiple colors are present, multiplicity is both 1 and greater than 1
        color3 = BGGenome("genome3")
        multicolor = Multicolor(color1, color1, color1, color2, color2, color3)
        edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        result = edge.to_json(schema_info=False)
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(result["vertex1_id"], v1.json_id)
        self.assertEqual(result["vertex2_id"], v2.json_id)
        self.assertSetEqual(set(result["multicolor"]), {color1.json_id, color2.json_id, color3.json_id})
        self.assertDictEqual(Counter(result["multicolor"]), Counter(color.json_id for color in multicolor.multicolors.elements()))
        # weird case when a vertex1/vertex attribute in edge is not an instance of BGVertex
        # and moreover it does not have "json_id" attribute
        edge = BGEdge(vertex1=v1, vertex2=1, multicolor=Multicolor(color1))
        result = edge.to_json()
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(result["vertex1_id"], v1.json_id)
        self.assertEqual(result["vertex2_id"], hash(1))
        self.assertListEqual(result["multicolor"], [color1.json_id])
        self.assertEqual(result[BGEdge_JSON_SCHEMA_JSON_KEY], edge.json_schema_name)

    def test_json_deserialization_default_schema(self):
        # with no scheme is supplied, default scheme for the BGVertex is applied
        # deserialization for vertices and multicolor shall be performed as is, but then it will be resupplied from
        # the overviewing BreakpointGraph
        # correct case no information in json object about schema
        json_object = {
            "vertex1_id": 1,
            "vertex2_id": 2,
            "multicolor": [1, 2, 3, 4]
        }
        result = BGEdge.from_json(data=json_object)
        self.assertTrue(isinstance(result, BGEdge))
        self.assertEqual(result.vertex1, 1)
        self.assertEqual(result.vertex2, 2)
        self.assertListEqual(result.multicolor, [1, 2, 3, 4])
        # correct case with information about json object schema
        # such information about json schema shall be ignored at the BGEdge deserialization level
        json_object = {
            BGEdge_JSON_SCHEMA_JSON_KEY: "dummy_string",
            "vertex1_id": 1,
            "vertex2_id": 2,
            "multicolor": [1, 2, 3, 4]
        }
        result = BGEdge.from_json(data=json_object)
        self.assertTrue(isinstance(result, BGEdge))
        self.assertEqual(result.vertex1, 1)
        self.assertEqual(result.vertex2, 2)
        self.assertListEqual(result.multicolor, [1, 2, 3, 4])
        # incorrect case with at least one vertex id not present in json object
        json_object = {
            "vertex2_id": 2,
            "multicolor": [1, 2, 3, 4]
        }
        with self.assertRaises(ValueError):
            BGEdge.from_json(data=json_object)
        json_object = {
            "vertex1_id": 2,
            "multicolor": [1, 2, 3, 4]
        }
        with self.assertRaises(ValueError):
            BGEdge.from_json(data=json_object)
        # incorrect case with no multicolor present in json object
        json_object = {
            "vertex2_id": 2,
            "vertex1_id": 1,
        }
        with self.assertRaises(ValueError):
            BGEdge.from_json(data=json_object)

    def test_json_deserialization_supplied_schema(self):
        # when a scheme is supplied it shall be used for deserialization
        # correct case no information in json object about schema
        class BGEdgeJSONSchemeDefaultVertex1(BGEdge.BGEdgeJSONSchema):
            def make_object(self, data):
                if "vertex1_json_id" not in data:
                    data["vertex1_json_id"] = 1
                return super(BGEdgeJSONSchemeDefaultVertex1, self).make_object(data)

        json_object = {
            "vertex1_id": 1,
            "vertex2_id": 2,
            "multicolor": [1, 2, 3, 4]
        }
        result = BGEdge.from_json(data=json_object, json_schema_class=BGEdgeJSONSchemeDefaultVertex1)
        self.assertTrue(isinstance(result, BGEdge))
        self.assertEqual(result.vertex1, 1)
        self.assertEqual(result.vertex2, 2)
        self.assertListEqual(result.multicolor, [1, 2, 3, 4])
        # correct case with information about json object schema
        # such information about json schema shall be ignored at the BGEdge deserialization level
        json_object = {
            BGEdge_JSON_SCHEMA_JSON_KEY: "dummy_string",
            "vertex1_id": 1,
            "vertex2_id": 2,
            "multicolor": [1, 2, 3, 4]
        }
        result = BGEdge.from_json(data=json_object, json_schema_class=BGEdgeJSONSchemeDefaultVertex1)
        self.assertTrue(isinstance(result, BGEdge))
        self.assertEqual(result.vertex1, 1)
        self.assertEqual(result.vertex2, 2)
        self.assertListEqual(result.multicolor, [1, 2, 3, 4])
        # incorrect case with at least one vertex id not present in json object
        json_object = {
            "vertex2_id": 2,
            "multicolor": [1, 2, 3, 4]
        }
        result = BGEdge.from_json(data=json_object, json_schema_class=BGEdgeJSONSchemeDefaultVertex1)
        self.assertTrue(isinstance(result, BGEdge))
        self.assertEqual(result.vertex1, 1)
        self.assertEqual(result.vertex2, 2)
        self.assertListEqual(result.multicolor, [1, 2, 3, 4])
        json_object = {
            "vertex1_id": 2,
            "multicolor": [1, 2, 3, 4]
        }
        with self.assertRaises(ValueError):
            BGEdge.from_json(data=json_object)
        # incorrect case with no multicolor present in json object
        json_object = {
            "vertex2_id": 2,
            "vertex1_id": 1,
        }
        with self.assertRaises(ValueError):
            BGEdge.from_json(data=json_object)

    def test_initialization_empty_data_attribute(self):
        v1 = TaggedBlockVertex("v1")
        v2 = TaggedBlockVertex("v2")
        multicolor = Multicolor(self.genome1)
        edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        self.assertDictEqual(edge.data, BGEdge.create_default_data_dict())

    def test_initialization_non_empty_data_attribute(self):
        v1 = TaggedBlockVertex("v1")
        v2 = TaggedBlockVertex("v2")
        multicolor = Multicolor(self.genome1)
        data = {
            "fragment": {"name": "scaffold1"}

        }
        edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor, data=data)
        self.assertDictEqual(edge.data, data)

    def test_data_update(self):
        update_source = {"fragment": {"name": "scaffold11"}}
        edge = BGEdge(vertex1=TaggedBlockVertex("v1"), vertex2=TaggedBlockVertex("v2"),
                      multicolor=Multicolor(self.genome1, self.genome2),
                      data={"fragment": {"name": "scaffold2", "origin": "test"}})
        edge.update_data(source=update_source)
        self.assertIsInstance(edge.data, dict)
        self.assertIn("fragment", edge.data)
        self.assertIsInstance(edge.data["fragment"], dict)
        self.assertIn("name", edge.data["fragment"])
        self.assertIn("origin", edge.data["fragment"])
        self.assertEqual(edge.data["fragment"]["name"], "scaffold11")
        self.assertEqual(edge.data["fragment"]["origin"], "test")

    def test_data_update_empty_source(self):
        edge = BGEdge(vertex1=TaggedBlockVertex("v1"), vertex2=TaggedBlockVertex("v2"),
                      multicolor=Multicolor(self.genome1, self.genome2),
                      data={"fragment": {"name": "scaffold2", "origin": "test"}})
        update_source = {}
        edge.update_data(source=update_source)
        self.assertTrue(dicts_are_equal(edge.data, {"fragment": {"name": "scaffold2", "origin": "test"}}))

    def test_data_update_non_dict_source(self):
        edge = BGEdge(vertex1=TaggedBlockVertex("v1"), vertex2=TaggedBlockVertex("v2"),
                      multicolor=Multicolor(self.genome1, self.genome2),
                      data={"fragment": {"name": "scaffold2", "origin": "test"}})
        for source in [1, "2", Multicolor(), (1, ), [2, ]]:
            with self.assertRaises(ValueError):
                edge.update_data(source=source)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()  # pragma: no cover
