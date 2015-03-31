# -*- coding: utf-8 -*-
from collections import Counter
import types
from unittest.mock import Mock
from bg.genome import BGGenome
from bg.multicolor import Multicolor
from bg.vertex import BGVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.edge import BGEdge


class BGEdgeTestCase(unittest.TestCase):

    def setUp(self):
        self.genome1 = BGGenome("red")
        self.genome2 = BGGenome("green")
        self.genome3 = BGGenome("blue")
        self.genome4 = BGGenome("black")
        self.genome4 = BGGenome("yellow")

    def test_empty_initialization_incorrect(self):
        with self.assertRaises(TypeError):
            BGEdge()

    def test_initialization(self):
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor(self.genome3)
        edge = BGEdge(vertex1=v1,
                      vertex2=v2,
                      multicolor=multicolor)
        self.assertEqual(edge.vertex1, v1)
        self.assertEqual(edge.vertex2, v2)
        self.assertEqual(edge.multicolor, multicolor)

    def test_merging_correct(self):
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor(self.genome3)
        multicolor1 = Multicolor(self.genome2)
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        edge2 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor1)
        merged_edge = BGEdge.merge(edge1, edge2)
        self.assertEqual(merged_edge.vertex1, v1)
        self.assertEqual(merged_edge.vertex2, v2)
        self.assertEqual(merged_edge.multicolor, multicolor + multicolor1)

    def test_merging_incorrect(self):
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        v3 = BGVertex("v3")
        v4 = BGVertex("v4")
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
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        v3 = BGVertex("v3")
        v4 = BGVertex("v4")
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

    def test_is_infinity_edge(self):
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        v3 = BGVertex("v3__infinity")
        multicolor = Multicolor(self.genome3)
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        edge2 = BGEdge(vertex1=v1, vertex2=v3, multicolor=multicolor)
        edge3 = BGEdge(vertex1=v3, vertex2=v1, multicolor=multicolor)
        edge4 = BGEdge(vertex1=v3, vertex2=v3, multicolor=multicolor)
        self.assertFalse(edge1.is_infinity_edge)
        self.assertTrue(edge2.is_infinity_edge)
        self.assertTrue(edge3.is_infinity_edge)
        self.assertTrue(edge4.is_infinity_edge)

    def test_iter_over_colors_json_ids(self):
        # when multiedge is serialized into json a list of colors in it referenced by their ids
        # the multiplicity of colors has to be preserved
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
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
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
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
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
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
        v1, v2 = BGVertex("v1"), BGVertex("v2")
        color1 = BGGenome("genome1")
        multicolor = Multicolor(color1)
        edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        ref_result = {
            "vertex1_id": v1.json_id,
            "vertex2_id": v2.json_id,
            "multicolor": [color1.json_id]
        }
        self.assertDictEqual(edge.to_json(), ref_result)
        # case where multiple colors are present, multiplicity is 1 for every of them
        color2 = BGGenome("genome2")
        multicolor = Multicolor(color1, color2)
        edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        result = edge.to_json()
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(result["vertex1_id"], v1.json_id)
        self.assertEqual(result["vertex2_id"], v2.json_id)
        self.assertSetEqual(set(result["multicolor"]), {color1.json_id, color2.json_id})
        # case where multiple colors are present, multiplicity is both 1 and greater than 1
        color3 = BGGenome("genome3")
        multicolor = Multicolor(color1, color1, color1, color2, color2, color3)
        edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        result = edge.to_json()
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


if __name__ == '__main__':  # pragma: no cover
    unittest.main()         # pragma: no cover
