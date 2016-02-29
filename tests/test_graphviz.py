import unittest
from unittest.mock import *

import collections

from bg import BlockVertex, InfinityVertex
from bg.graphviz import NodeShapeProcessor


class NodeShapeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultNodeShapeProcessor = NodeShapeProcessor()

    def test_default_shape(self):
        self.assertEqual("circle", self.defaultNodeShapeProcessor.get_shape())

    def test_default_shape_for_regular_non_bg_vertex(self):
        for vertex in [1, "1", (1,), Mock(spec=collections.Hashable)]:
            self.assertEqual("circle", self.defaultNodeShapeProcessor.get_shape(vertex))

    def test_default_shape_for_regular_bg_vertex(self):
        self.assertEqual("circle", self.defaultNodeShapeProcessor.get_shape(vertex=BlockVertex(name="test")))

    def test_default_shape_for_irregular_bg_vertex(self):
        self.assertEqual("point", self.defaultNodeShapeProcessor.get_shape(vertex=InfinityVertex(name="test")))


if __name__ == '__main__':
    unittest.main()
