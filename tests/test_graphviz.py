import unittest
from unittest.mock import *

import collections

from bg.edge import BGEdge
from bg.multicolor import Multicolor
from bg.graphviz import VertexShapeProcessor, VertexTextProcessor, VertexProcessor, EdgeShapeProcessor, EdgeProcessor
from bg.vertices import TaggedBlockVertex, TaggedInfinityVertex, BlockVertex, InfinityVertex


class VertexShapeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultVertexShapeProcessor = VertexShapeProcessor()

    def test_default_shape(self):
        self.assertEqual("oval", self.defaultVertexShapeProcessor.get_shape())

    def test_default_shape_for_regular_non_bg_vertex(self):
        for vertex in [1, "1", (1,), Mock(spec=collections.Hashable), Mock(spec=TaggedBlockVertex)]:
            self.assertEqual("oval", self.defaultVertexShapeProcessor.get_shape(vertex))

    def test_default_shape_for_regular_bg_vertex(self):
        self.assertEqual("oval", self.defaultVertexShapeProcessor.get_shape(vertex=BlockVertex(name="test")))

    def test_default_shape_for_irregular_bg_vertex(self):
        self.assertEqual("point", self.defaultVertexShapeProcessor.get_shape(vertex=InfinityVertex(name="test")))

    def test_default_pen_width(self):
        self.assertEqual(1, self.defaultVertexShapeProcessor.get_pen_width())

    def test_pen_width_label(self):
        self.assertEqual("penwidth", self.defaultVertexShapeProcessor.pen_width_label)

    def test_shape_label(self):
        self.assertEqual("shape", self.defaultVertexShapeProcessor.shape_label)


class VertexTextProcessingTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultVertexTextProcessor = VertexTextProcessor()

    def test_default_text_font(self):
        self.assertEqual("Arial", self.defaultVertexTextProcessor.get_text_font())

    def test_default_text_size(self):
        self.assertEqual(12, self.defaultVertexTextProcessor.get_text_size())

    def test_default_text_color(self):
        self.assertEqual("black", self.defaultVertexTextProcessor.get_text_color())


class VertexProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultVertexProcessor = VertexProcessor()

    def test_default_vertex_shape_processor_field(self):
        self.assertIsInstance(self.defaultVertexProcessor.shape_processor, VertexShapeProcessor)

    def test_default_vertex_text_processor(self):
        self.assertIsInstance(self.defaultVertexProcessor.text_processor, VertexTextProcessor)


class EdgeShapeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultEdgeShapeProcessor = EdgeShapeProcessor()
        self.regular_vertex = TaggedBlockVertex(1)
        self.regular_vertex2 = TaggedBlockVertex(2)
        self.edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.regular_vertex2, multicolor=Multicolor())
        self.irregular_vertex = InfinityVertex("v1")
        self.ir_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.irregular_vertex, multicolor=Multicolor())
        self.repeat_vertex = TaggedInfinityVertex("v1")
        self.repeat_vertex.add_tag("repeat", "rrr1")
        self.r_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.repeat_vertex, multicolor=Multicolor())

    def test_default_style(self):
        self.assertEqual("solid", self.defaultEdgeShapeProcessor.get_style())

    def test_default_regular_edge_style(self):
        self.assertEqual("solid", self.defaultEdgeShapeProcessor.get_style(self.edge))

    def test_default_irregular_edge_style(self):
        self.assertEqual("dotted", self.defaultEdgeShapeProcessor.get_style(self.ir_edge))

    def test_default_repeat_edge_style(self):
        self.assertEqual("dashed", self.defaultEdgeShapeProcessor.get_style(self.r_edge))

    def test_default_pen_width(self):
        self.assertEqual(1, self.defaultEdgeShapeProcessor.get_pen_width())

    def test_default_regular_edge_pen_width(self):
        self.assertEqual(1, self.defaultEdgeShapeProcessor.get_pen_width(self.edge))

    def test_default_irregular_edge_pen_width(self):
        self.assertEqual(.1, self.defaultEdgeShapeProcessor.get_pen_width(self.ir_edge))

    def test_default_repeat_edge_pen_width(self):
        self.assertEqual(.5, self.defaultEdgeShapeProcessor.get_pen_width(self.r_edge))

    def test_default_direction(self):
        self.assertEqual("none", self.defaultEdgeShapeProcessor.get_dir_type())

    def test_default_regular_edge_direction(self):
        self.assertEqual("none", self.defaultEdgeShapeProcessor.get_dir_type(self.edge))

    def test_default_irregular_edge_direction(self):
        self.assertEqual("none", self.defaultEdgeShapeProcessor.get_dir_type(self.ir_edge))

    def test_default_repeat_edge_direction(self):
        self.assertEqual("none", self.defaultEdgeShapeProcessor.get_dir_type(self.r_edge))


class EdgeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultEdgeProcessor = EdgeProcessor()
        self.regular_vertex = TaggedBlockVertex(1)
        self.regular_vertex2 = TaggedBlockVertex(2)
        self.edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.regular_vertex2, multicolor=Multicolor())
        self.irregular_vertex = InfinityVertex("v1")
        self.ir_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.irregular_vertex, multicolor=Multicolor())
        self.repeat_vertex = TaggedInfinityVertex("v1")
        self.repeat_vertex.add_tag("repeat", "rrr1")
        self.r_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.repeat_vertex, multicolor=Multicolor())

    def test_edge_shape_processor_field(self):
        self.assertIsInstance(self.defaultEdgeProcessor.edge_shape_processor, EdgeShapeProcessor)


if __name__ == '__main__':
    unittest.main()
