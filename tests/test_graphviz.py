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

    def test_shape_attrib_template(self):
        self.assertEqual("shape=\"{shape}\"", self.defaultVertexShapeProcessor.shape_attrib_template)

    def test_default_pen_width(self):
        self.assertEqual(1, self.defaultVertexShapeProcessor.get_pen_width())

    def test_pen_width_attrib_template(self):
        self.assertEqual("penwidth=\"{pen_width}\"", self.defaultVertexShapeProcessor.pen_width_attrib_template)


class VertexTextProcessingTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultVertexTextProcessor = VertexTextProcessor()

    def test_default_text_font(self):
        self.assertEqual("Arial", self.defaultVertexTextProcessor.get_text_font())

    def test_default_text_size(self):
        self.assertEqual(12, self.defaultVertexTextProcessor.get_text_size())

    def test_default_text_color(self):
        self.assertEqual("black", self.defaultVertexTextProcessor.get_text_color())

    def test_label_attrib_template(self):
        self.assertEqual("label={label}", self.defaultVertexTextProcessor.label_attrib_template)

    def text_color_attrib_template(self):
        self.assertEqual("fontcolor=\"{color}\"", self.defaultVertexTextProcessor.color_attrib_template)

    def test_font_attrib_template(self):
        self.assertEqual("font=\"{font}\"", self.defaultVertexTextProcessor.font_attrib_template)

    def text_size_attrib_template(self):
        self.assertEqual("size=\"{size}\"", self.defaultVertexTextProcessor.size_attrib_template)

    def test_vertex_name_plain_text(self):
        regular_vertex = TaggedBlockVertex(name="namet")
        self.assertEqual("\"namet\"", self.defaultVertexTextProcessor.get_text(vertex=regular_vertex))
        self.assertEqual("\"namet\"", self.defaultVertexTextProcessor.get_text(vertex=regular_vertex, text_format="plain"))
        self.assertEqual("\"namet\"",
                         self.defaultVertexTextProcessor.get_text(vertex=regular_vertex, text_format=VertexTextProcessor.VertexTextType.plain))

    def test_vertex_name_html_text(self):
        regular_vertex = TaggedBlockVertex(name="namet")
        self.assertEqual("<name<SUP>t</SUP>>", self.defaultVertexTextProcessor.get_text(vertex=regular_vertex, text_format="html"))
        self.assertEqual("<name<SUP>t</SUP>>", self.defaultVertexTextProcessor.get_text(vertex=regular_vertex, text_format=VertexTextProcessor.VertexTextType.html))
        self.assertEqual("<namet>", self.defaultVertexTextProcessor.get_text(vertex="namet", text_format=VertexTextProcessor.VertexTextType.html))

    def test_tagged_vertex_name_plain(self):
        tagged_vertex = TaggedBlockVertex(name="namet")
        tagged_vertex.add_tag("tag1", 10)
        tagged_vertex.add_tag("tag2", 20)
        self.assertEqual("\"namet (tag1:10) (tag2:20)\"", self.defaultVertexTextProcessor.get_text(vertex=tagged_vertex))
        self.assertEqual("\"namet (tag1:10) (tag2:20)\"", self.defaultVertexTextProcessor.get_text(vertex=tagged_vertex, text_format="plain"))

    def test_tagged_vertex_name_html(self):
        tagged_vertex = TaggedBlockVertex(name="namet")
        tagged_vertex.add_tag("tag1", 10)
        tagged_vertex.add_tag("tag2", 20)
        self.assertEqual("<name<SUP>t</SUP> (tag1:10) (tag2:20)>", self.defaultVertexTextProcessor.get_text(vertex=tagged_vertex, text_format="html"))


class VertexProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultVertexProcessor = VertexProcessor()

    def test_default_vertex_shape_processor_field(self):
        self.assertIsInstance(self.defaultVertexProcessor.shape_processor, VertexShapeProcessor)

    def test_default_vertex_text_processor(self):
        self.assertIsInstance(self.defaultVertexProcessor.text_processor, VertexTextProcessor)

    def test_overall_template(self):
        self.assertEqual("{v_id} [{attributes}];", self.defaultVertexProcessor.template)

    def test_getting_non_bg_vertex_id(self):
        vertex = "1"
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))  # consecutive access shall return previously assigned id
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))  # consecutive access shall return previously assigned id

        vertex = "3"
        self.assertEqual(2, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))
        self.assertEqual(2, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))
        self.assertEqual(2, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))

        vertex = "1"
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))

    def test_getting_bg_vertex_id(self):
        vertex1 = TaggedBlockVertex(name="test")
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex1))
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex1))
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex1))

        vertex2 = TaggedBlockVertex(name="test")
        self.assertFalse(vertex1 is vertex2)
        self.assertFalse(vertex2 is vertex1)
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex2))
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex1))

        vertex3 = TaggedBlockVertex(name="test")
        vertex3.add_tag("tag", 1)
        self.assertNotEqual(self.defaultVertexProcessor.get_vertex_id(vertex=vertex1),
                            self.defaultVertexProcessor.get_vertex_id(vertex=vertex3))
        self.assertEqual(2, self.defaultVertexProcessor.get_vertex_id(vertex=vertex3))

    def test_getting_bg_vertex_id_large_number(self):
        indexed_vertices = [(number, TaggedBlockVertex(number)) for number in range(1, 100000)]
        for index, vertex in indexed_vertices:
            self.assertEqual(index, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))


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
