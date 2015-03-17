# -*- coding: utf-8 -*-
from bg.multicolor import Multicolor
from bg.vertex import BGVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest
from bg.edge import BGEdge


class BGEdgeTestCase(unittest.TestCase):
    def test_empty_initialization_incorrect(self):
        with self.assertRaises(TypeError):
            BGEdge()

    def test_initialization(self):
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("blue")
        edge = BGEdge(vertex1=v1,
                      vertex2=v2,
                      multicolor=multicolor)
        self.assertEqual(edge.vertex1, v1)
        self.assertEqual(edge.vertex2, v2)
        self.assertEqual(edge.multicolor, multicolor)

    def test_merging_correct(self):
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("blue")
        multicolor1 = Multicolor("green")
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
        multicolor = Multicolor("blue")
        multicolor1 = Multicolor("green")
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
        multicolor = Multicolor("blue")
        multicolor1 = Multicolor("green")
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
        multicolor = Multicolor("blue")
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        edge2 = BGEdge(vertex1=v1, vertex2=v3, multicolor=multicolor)
        edge3 = BGEdge(vertex1=v3, vertex2=v1, multicolor=multicolor)
        edge4 = BGEdge(vertex1=v3, vertex2=v3, multicolor=multicolor)
        self.assertFalse(edge1.is_infinity_edge)
        self.assertTrue(edge2.is_infinity_edge)
        self.assertTrue(edge3.is_infinity_edge)
        self.assertTrue(edge4.is_infinity_edge)



if __name__ == '__main__':  # pragma: no cover
    unittest.main()         # pragma: no cover
