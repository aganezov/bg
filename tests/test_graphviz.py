import unittest
from unittest.mock import *

import collections

from bg import BGGenome
from bg.edge import BGEdge
from bg.multicolor import Multicolor
from bg.graphviz import VertexShapeProcessor, VertexTextProcessor, VertexProcessor, EdgeShapeProcessor, EdgeProcessor, EdgeTextProcessor
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

    def test_get_all_attributes_as_list_of_strings_regular_vertex(self):
        vertex = TaggedBlockVertex("10t")
        self.assertSetEqual({"shape=\"oval\"", "penwidth=\"1\""}, set(self.defaultVertexShapeProcessor.get_attributes_string_list(vertex=vertex)))

    def test_get_all_attributes_as_list_of_strings_irregular_vertex(self):
        vertex = TaggedInfinityVertex("10t")
        self.assertSetEqual({"shape=\"point\"", "penwidth=\"1\""}, set(self.defaultVertexShapeProcessor.get_attributes_string_list(vertex=vertex)))


class VertexTextProcessorTestCase(unittest.TestCase):
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
        self.assertEqual("fontname=\"{font}\"", self.defaultVertexTextProcessor.font_attrib_template)

    def text_size_attrib_template(self):
        self.assertEqual("fontsize=\"{size}\"", self.defaultVertexTextProcessor.size_attrib_template)

    def test_vertex_name_plain_text(self):
        regular_vertex = TaggedBlockVertex(name="namet")
        self.assertEqual("\"namet\"", self.defaultVertexTextProcessor.get_text(vertex=regular_vertex))
        self.assertEqual("\"namet\"", self.defaultVertexTextProcessor.get_text(vertex=regular_vertex, label_format="plain"))
        self.assertEqual("\"namet\"",
                         self.defaultVertexTextProcessor.get_text(vertex=regular_vertex, label_format=VertexTextProcessor.VertexTextType.plain))

    def test_vertex_name_html_text(self):
        regular_vertex = TaggedBlockVertex(name="namet")
        self.assertEqual("<name<SUP>t</SUP>>", self.defaultVertexTextProcessor.get_text(vertex=regular_vertex, label_format="html"))
        self.assertEqual("<name<SUP>t</SUP>>",
                         self.defaultVertexTextProcessor.get_text(vertex=regular_vertex, label_format=VertexTextProcessor.VertexTextType.html))
        self.assertEqual("<namet>", self.defaultVertexTextProcessor.get_text(vertex="namet", label_format=VertexTextProcessor.VertexTextType.html))

    def test_tagged_vertex_name_plain(self):
        tagged_vertex = TaggedBlockVertex(name="namet")
        tagged_vertex.add_tag("tag1", 10)
        tagged_vertex.add_tag("tag2", 20)
        self.assertEqual("\"namet (tag1:10) (tag2:20)\"", self.defaultVertexTextProcessor.get_text(vertex=tagged_vertex))
        self.assertEqual("\"namet (tag1:10) (tag2:20)\"", self.defaultVertexTextProcessor.get_text(vertex=tagged_vertex, label_format="plain"))

    def test_tagged_vertex_name_html(self):
        tagged_vertex = TaggedBlockVertex(name="namet")
        tagged_vertex.add_tag("tag1", 10)
        tagged_vertex.add_tag("tag2", 20)
        self.assertEqual("<name<SUP>t</SUP> (tag1:10) (tag2:20)>", self.defaultVertexTextProcessor.get_text(vertex=tagged_vertex, label_format="html"))

    def test_get_all_attributes_as_list_of_strings_regular_vertex(self):
        vertex = TaggedBlockVertex("10t")
        self.assertSetEqual({"label=\"10t\"", "fontname=\"Arial\"", "fontsize=\"12\"", "fontcolor=\"black\""},
                            set(self.defaultVertexTextProcessor.get_attributes_string_list(vertex=vertex)))
        self.assertSetEqual({"label=\"10t\"", "fontname=\"Arial\"", "fontsize=\"12\"", "fontcolor=\"black\""},
                            set(self.defaultVertexTextProcessor.get_attributes_string_list(vertex=vertex, label_format="plain")))


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

    def test_getting_irregular_bg_vertices_same_blcok_different_tags(self):
        ir_vertex1 = TaggedInfinityVertex("10t")
        ir_vertex2 = TaggedInfinityVertex("10t")
        ir_vertex1.add_tag("repeat", "1h")
        ir_vertex2.add_tag("repeat", "100h")
        irv1_id = self.defaultVertexProcessor.get_vertex_id(vertex=ir_vertex1)
        irv2_id = self.defaultVertexProcessor.get_vertex_id(vertex=ir_vertex2)
        self.assertEqual(irv1_id, irv2_id)

    def test_getting_bg_vertex_id_large_number(self):
        indexed_vertices = [(number, TaggedBlockVertex(number)) for number in range(1, 100000)]
        for index, vertex in indexed_vertices:
            self.assertEqual(index, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))

    def test_full_regular_vertex_graphviz_export_all_default(self):
        vertex = TaggedBlockVertex("10t")
        self.assertEqual("1 [label=\"10t\", fontname=\"Arial\", fontsize=\"12\", fontcolor=\"black\", shape=\"oval\", penwidth=\"1\"];",
                         self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex))
        self.assertEqual("1 [label=<10<SUP>t</SUP>>, fontname=\"Arial\", fontsize=\"12\", fontcolor=\"black\", shape=\"oval\", penwidth=\"1\"];",
                         self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex, label_format="html"))

    def test_full_regular_vertex_with_tags_export_all_default(self):
        vertex = TaggedBlockVertex("10t")
        vertex.add_tag("tag1", 1)
        vertex.add_tag("tag2", 2)
        self.assertEqual("1 [label=\"10t (tag1:1) (tag2:2)\", fontname=\"Arial\", fontsize=\"12\", fontcolor=\"black\", shape=\"oval\", penwidth=\"1\"];",
                                                                                         self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex))
        self.assertEqual(
            "1 [label=<10<SUP>t</SUP> (tag1:1) (tag2:2)>, fontname=\"Arial\", fontsize=\"12\", fontcolor=\"black\", shape=\"oval\", penwidth=\"1\"];",
            self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex, label_format="html"))

    def test_full_irregular_vertex_graphviz_entry_all_default(self):
        vertex = TaggedInfinityVertex("10t")
        self.assertEqual("1 [shape=\"point\", penwidth=\"1\"];", self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex))
        self.assertEqual("1 [shape=\"point\", penwidth=\"1\"];", self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex, label_format="html"))


class EdgeShapeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultEdgeShapeProcessor = EdgeShapeProcessor()
        self.regular_vertex = TaggedBlockVertex(1)
        self.regular_vertex2 = TaggedBlockVertex(2)
        self.color1 = BGGenome("genome1")
        self.color2 = BGGenome("genome2")
        self.edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.regular_vertex2, multicolor=Multicolor(self.color1))
        self.irregular_vertex = InfinityVertex("v1")
        self.ir_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.irregular_vertex, multicolor=Multicolor(self.color1))
        self.repeat_vertex = TaggedInfinityVertex("v1")
        self.repeat_vertex.add_tag("repeat", "rrr1")
        self.r_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.repeat_vertex, multicolor=Multicolor(self.color1))

    def test_default_style(self):
        self.assertEqual("solid", self.defaultEdgeShapeProcessor.get_style())

    def test_default_regular_edge_style(self):
        self.assertEqual("solid", self.defaultEdgeShapeProcessor.get_style(self.edge))

    def test_default_irregular_edge_style(self):
        self.assertEqual("dotted", self.defaultEdgeShapeProcessor.get_style(self.ir_edge))

    def test_default_repeat_edge_style(self):
        self.assertEqual("dashed", self.defaultEdgeShapeProcessor.get_style(self.r_edge))

    def test_style_attribute_template(self):
        self.assertEqual("style=\"{style}\"", self.defaultEdgeShapeProcessor.style_attribute_template)

    def test_default_pen_width(self):
        self.assertEqual(1, self.defaultEdgeShapeProcessor.get_pen_width())

    def test_pen_width_attribute_template(self):
        self.assertEqual("penwidth=\"{pen_width}\"", self.defaultEdgeShapeProcessor.pen_width_attribute_template)

    def test_default_regular_edge_pen_width(self):
        self.assertEqual(1, self.defaultEdgeShapeProcessor.get_pen_width(self.edge))

    def test_default_irregular_edge_pen_width(self):
        self.assertEqual(.1, self.defaultEdgeShapeProcessor.get_pen_width(self.ir_edge))

    def test_default_repeat_edge_pen_width(self):
        self.assertEqual(.5, self.defaultEdgeShapeProcessor.get_pen_width(self.r_edge))

    def test_get_dot_colors_for_multicolor_single_color(self):
        mc = Multicolor(BGGenome("genome1"))
        dot_colors = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc)
        self.assertEqual(len(dot_colors), 1)
        self.assertEqual(len(set(dot_colors)), 1)
        dot_color = dot_colors[0]
        self.assertIn(dot_color, EdgeShapeProcessor.EdgeColors)
        mc2 = Multicolor(BGGenome("genome1"))
        dot_colors2 = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc2)
        self.assertListEqual(dot_colors, dot_colors2)

    def test_get_dot_colors_for_multicolor_multiple_colors(self):
        mc = Multicolor(BGGenome("genome1"), BGGenome("genome2"), BGGenome("genome3"))
        dot_colors = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc)
        self.assertEqual(len(dot_colors), 3)
        self.assertEqual(len(set(dot_colors)), 3)
        for dot_color in dot_colors:
            self.assertIn(dot_color, self.defaultEdgeShapeProcessor.EdgeColors)
        mc2 = Multicolor(BGGenome("genome1"), BGGenome("genome2"))
        mc3 = Multicolor(BGGenome("genome3"))
        dot_colors2 = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc2)
        dot_colors3 = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc3)
        self.assertTrue(set(dot_colors2).issubset(dot_colors))
        self.assertTrue(set(dot_colors3).issubset(dot_colors))

    def test_get_dot_colors_for_multicolor_single_color_with_greater_multiplicity(self):
        mc = Multicolor(BGGenome("genome1"), BGGenome("genome1"), BGGenome("genome1"))
        dot_colors = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc)
        self.assertEqual(len(dot_colors), 3)
        self.assertEqual(len(set(dot_colors)), 1)
        dot_color = set(dot_colors).pop()
        self.assertIn(dot_color, self.defaultEdgeShapeProcessor.EdgeColors)
        mc2 = Multicolor(BGGenome("genome1"), BGGenome("genome1"))
        dot_colors2 = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc2)
        self.assertEqual(len(dot_colors2), 2)
        self.assertEqual(len(set(dot_colors2)), 1)
        self.assertSetEqual(set(dot_colors2), set(dot_colors))

    def test_get_dot_colors_for_multicolor_multiple_colors_with_greater_multiplicity(self):
        mc = Multicolor(BGGenome("genome1"), BGGenome("genome1"), BGGenome("genome1"), BGGenome("genome2"), BGGenome("genome2"), BGGenome("genome3"))
        dot_colors = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc)
        self.assertEqual(len(dot_colors), 6)
        self.assertEqual(len(set(dot_colors)), 3)
        for color in dot_colors:
            self.assertIn(color, self.defaultEdgeShapeProcessor.EdgeColors)
        mc2 = Multicolor(BGGenome("genome1"), BGGenome("genome1"))
        mc3 = Multicolor(BGGenome("genome2"), BGGenome("genome1"), BGGenome("genome2"))
        dot_colors2 = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc2)
        dot_colors3 = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc3)
        self.assertEqual(len(dot_colors2), 2)
        self.assertEqual(len(set(dot_colors2)), 1)
        self.assertEqual(len(dot_colors3), 3)
        self.assertEqual(len(set(dot_colors3)), 2)
        self.assertTrue(set(dot_colors2).issubset(set(dot_colors)))
        self.assertTrue(set(dot_colors3).issubset(set(dot_colors)))

    def test_color_attribute_template(self):
        self.assertEqual("color=\"{color}\"", self.defaultEdgeShapeProcessor.color_attribute_template)

    def test_get_all_attributes_as_list_of_strings_regular_edge(self):
        color = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=Multicolor(self.color1))[0]
        self.assertSetEqual({"color=\"" + color.value + "\"", "style=\"solid\"", "penwidth=\"1\""},
                            set(self.defaultEdgeShapeProcessor.get_attributes_string_list(edge=self.edge)))

    def test_get_all_attributes_as_list_of_strings_irregular_edge(self):
        color = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=Multicolor(self.color1))[0]
        self.assertSetEqual({"color=\"" + color.value + "\"", "style=\"dotted\"", "penwidth=\"0.1\""},
                            set(self.defaultEdgeShapeProcessor.get_attributes_string_list(edge=self.ir_edge)))

    def test_get_all_attributes_as_list_of_strings_repeat_edge(self):
        color = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=Multicolor(self.color1))[0]
        self.assertSetEqual({"color=\"" + color.value + "\"", "style=\"dashed\"", "penwidth=\"0.5\""},
                            set(self.defaultEdgeShapeProcessor.get_attributes_string_list(edge=self.r_edge)))

    def test_get_all_attribute_as_list_of_strings_multiedge_error(self):
        with self.assertRaises(ValueError):
            multiedge = BGEdge(vertex1=self.regular_vertex, vertex2=self.regular_vertex2, multicolor=Multicolor(self.color1, self.color2))
            self.defaultEdgeShapeProcessor.get_attributes_string_list(edge=multiedge)
        with self.assertRaises(ValueError):
            multiedge = BGEdge(vertex1=self.regular_vertex, vertex2=self.regular_vertex2, multicolor=Multicolor(self.color1, self.color1))
            self.defaultEdgeShapeProcessor.get_attributes_string_list(edge=multiedge)


class EdgeTextProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultEdgeTextProcessor = EdgeTextProcessor()
        self.regular_edge = BGEdge(vertex1=TaggedBlockVertex("10t"), vertex2=TaggedBlockVertex("11h"), multicolor=Multicolor())
        self.irregular_edge = BGEdge(vertex1=TaggedInfinityVertex("11h"), vertex2=TaggedBlockVertex("11h"), multicolor=Multicolor())
        repeat_irregular_vertex = TaggedInfinityVertex("11h")
        repeat_irregular_vertex.add_tag("repeat", "LLC1h")
        self.irregular_repeat_edge = BGEdge(vertex1=repeat_irregular_vertex, vertex2=TaggedBlockVertex("11h"), multicolor=Multicolor())

    def test_default_label_size(self):
        self.assertEqual(7, self.defaultEdgeTextProcessor.get_text_size(edge=self.regular_edge))
        self.assertEqual(7, self.defaultEdgeTextProcessor.get_text_size(edge=self.irregular_edge))
        self.assertEqual(7, self.defaultEdgeTextProcessor.get_text_size(edge=self.irregular_repeat_edge))

    def test_default_font(self):
        self.assertEqual("Arial", self.defaultEdgeTextProcessor.get_text_font_name(edge=self.regular_edge))
        self.assertEqual("Arial", self.defaultEdgeTextProcessor.get_text_font_name(edge=self.irregular_edge))
        self.assertEqual("Arial", self.defaultEdgeTextProcessor.get_text_font_name(edge=self.irregular_repeat_edge))

    def test_default_color(self):
        self.assertEqual("black", self.defaultEdgeTextProcessor.get_text_color(edge=self.regular_edge))
        self.assertEqual("black", self.defaultEdgeTextProcessor.get_text_color(edge=self.irregular_edge))
        self.assertEqual("black", self.defaultEdgeTextProcessor.get_text_color(edge=self.irregular_repeat_edge))

    def test_text_size_template(self):
        self.assertEqual("fontsize=\"{size}\"", self.defaultEdgeTextProcessor.size_attrib_template)

    def test_text_font_template(self):
        self.assertEqual("fontname=\"{font}\"", self.defaultEdgeTextProcessor.font_attrib_template)

    def test_text_color_template(self):
        self.assertEqual("fontcolor=\"{color}\"", self.defaultEdgeTextProcessor.color_attrib_template)

    def test_label_attrib_template(self):
        self.assertEqual("label={label}", self.defaultEdgeTextProcessor.label_attrib_template)

    def test_get_label_regular_edge_plain(self):
        self.assertEqual("\"\"", self.defaultEdgeTextProcessor.get_text(edge=self.regular_edge))
        self.assertEqual("\"\"", self.defaultEdgeTextProcessor.get_text(edge=self.regular_edge, label_format="plain"))

    def test_get_label_regular_edge_html(self):
        self.assertEqual("<>", self.defaultEdgeTextProcessor.get_text(edge=self.regular_edge, label_format="html"))

    def test_get_label_irregular_edge_plain(self):
        self.assertEqual("\"\"", self.defaultEdgeTextProcessor.get_text(edge=self.irregular_edge))
        self.assertEqual("\"\"", self.defaultEdgeTextProcessor.get_text(edge=self.irregular_edge, label_format="plain"))

    def test_get_label_irregular_edge_html(self):
        self.assertEqual("<>", self.defaultEdgeTextProcessor.get_text(edge=self.irregular_edge, label_format="html"))

    def test_get_label_irregular_repeat_edge_plain(self):
        self.assertEqual("\"r:LLC1h\"", self.defaultEdgeTextProcessor.get_text(edge=self.irregular_repeat_edge))
        self.assertEqual("\"r:LLC1h\"", self.defaultEdgeTextProcessor.get_text(edge=self.irregular_repeat_edge, label_format="plain"))

    def test_get_label_irregular_repeat_edge_html(self):
        self.assertEqual("<r:LLC1<SUP>h</SUP>>", self.defaultEdgeTextProcessor.get_text(edge=self.irregular_repeat_edge, label_format="html"))

    def test_get_attributes_as_string_list_regular_edge(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(edge=self.regular_edge)))
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(edge=self.regular_edge, label_format="plain")))

    def test_get_attributes_as_string_list_regular_edge_html(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=<>"},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(edge=self.regular_edge, label_format="html")))

    def test_get_attributes_as_string_list_irregular_edge(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(edge=self.irregular_edge)))
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(edge=self.regular_edge, label_format="plain")))

    def test_get_attributes_as_string_list_irregular_edge_html(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=<>"},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(edge=self.regular_edge, label_format="html")))

    def test_get_attributes_as_string_list_repeat_edge(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"r:LLC1h\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(edge=self.irregular_repeat_edge)))
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"r:LLC1h\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(edge=self.irregular_repeat_edge, label_format="plain")))

    def test_get_attributes_as_string_list_repeat_edge_html(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=<r:LLC1<SUP>h</SUP>>"},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(edge=self.irregular_repeat_edge, label_format="html")))


class EdgeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.vertex_processor = VertexProcessor()
        self.defaultEdgeProcessor = EdgeProcessor(vertex_processor=self.vertex_processor)
        self.regular_vertex = TaggedBlockVertex(1)
        self.regular_vertex2 = TaggedBlockVertex(2)
        self.edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.regular_vertex2, multicolor=Multicolor())
        self.irregular_vertex = InfinityVertex("v1")
        self.ir_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.irregular_vertex, multicolor=Multicolor())
        self.repeat_vertex = TaggedInfinityVertex("v1")
        self.repeat_vertex.add_tag("repeat", "rrr1")
        self.r_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.repeat_vertex, multicolor=Multicolor())

    def test_edge_shape_processor_field(self):
        self.assertIsInstance(self.defaultEdgeProcessor.shape_processor, EdgeShapeProcessor)

    def test_edge_text_processor_field(self):
        self.assertIsInstance(self.defaultEdgeProcessor.text_processor, EdgeTextProcessor)

    def test_full_regular_edge_graphviz_entry(self):
        v1_id = self.vertex_processor.get_vertex_id(self.edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.edge.vertex2)
        expected = str(v1_id) + " -- " + str(v2_id) + " [];"



if __name__ == '__main__':
    unittest.main()
