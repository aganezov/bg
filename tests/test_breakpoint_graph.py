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


if __name__ == '__main__':
    unittest.main()
