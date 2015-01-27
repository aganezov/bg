# -*- coding: utf-8 -*-
from bg.multicolor import Multicolor
from bg.vertex import BGVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

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

if __name__ == '__main__':
    unittest.main()
