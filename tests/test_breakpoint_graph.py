# -*- coding: utf-8 -*-
from bg.multicolor import Multicolor
from bg.vertex import BGVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.breakpoint_graph import BreakpointGraph


class BreakpointGraphTestCase(unittest.TestCase):
    def test_empty_initialization(self):
        graph = BreakpointGraph()
        self.assertEqual(len(graph.bg), 0)
        self.assertEqual(len(graph.bg.edges()), 0)

    def test_add_edge_without_multicolor(self):
        with self.assertRaises(TypeError):
            BreakpointGraph().add_edge(vertex1=BGVertex("v1"), vertex2=BGVertex("v2"))

    def test_add_edge(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("black")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        self.assertEqual(len(graph.bg), 2)
        self.assertEqual(len(graph.bg.edges()), 1)
        self.assertEqual(len(graph.bg.edges(v1)), 1)
        self.assertEqual(graph.bg.edges(v1, data=True)[0][2]["multicolor"], multicolor)
        self.assertEqual(graph.bg.edges(v1, data=True)[0][2]["multicolor"], multicolor)

    def test_add_edge_with_already_existing_merge(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("black")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        multicolor2 = Multicolor("green")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor2, merge=True)
        self.assertEqual(len(graph.bg), 2)
        self.assertEqual(len(graph.bg.edges()), 1)
        self.assertEqual(graph.bg.edges(v1, data=True)[0][2]["multicolor"], multicolor + multicolor2)
        multicolor3 = Multicolor("black")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor3, merge=True)
        self.assertEqual(len(graph.bg), 2)
        self.assertEqual(len(graph.bg.edges()), 1)
        self.assertEqual(graph.bg.edges(v1, data=True)[0][2]["multicolor"], multicolor + multicolor2)

if __name__ == '__main__':
    unittest.main()
