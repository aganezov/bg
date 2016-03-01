import unittest
from unittest.mock import *

import collections

from bg import BlockVertex, InfinityVertex
from bg.graphviz import NodeShapeProcessor, NodeTextProcessor, NodeProcessor


class NodeShapeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultNodeShapeProcessor = NodeShapeProcessor()

    def test_default_shape(self):
        self.assertEqual("oval", self.defaultNodeShapeProcessor.get_shape())

    def test_default_shape_for_regular_non_bg_vertex(self):
        for vertex in [1, "1", (1,), Mock(spec=collections.Hashable)]:
            self.assertEqual("oval", self.defaultNodeShapeProcessor.get_shape(vertex))

    def test_default_shape_for_regular_bg_vertex(self):
        self.assertEqual("oval", self.defaultNodeShapeProcessor.get_shape(vertex=BlockVertex(name="test")))

    def test_default_shape_for_irregular_bg_vertex(self):
        self.assertEqual("point", self.defaultNodeShapeProcessor.get_shape(vertex=InfinityVertex(name="test")))

    def test_default_pen_width(self):
        self.assertEqual(1, self.defaultNodeShapeProcessor.get_pen_width())


class NodeTextProcessingTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultNodeTextProcessor = NodeTextProcessor()

    def test_default_text_font(self):
        self.assertEqual("Arial", self.defaultNodeTextProcessor.get_text_font())

    def test_default_text_size(self):
        self.assertEqual(12, self.defaultNodeTextProcessor.get_text_size())

    def test_default_text_color(self):
        self.assertEqual("black", self.defaultNodeTextProcessor.get_text_color())


class NodeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultNodeProcessor = NodeProcessor()

    def test_default_node_shape_processor_field(self):
        self.assertIsInstance(self.defaultNodeProcessor.shape_processor, NodeShapeProcessor)

    def test_default_node_text_processor(self):
        self.assertIsInstance(self.defaultNodeProcessor.text_processor, NodeTextProcessor)


if __name__ == '__main__':
    unittest.main()
