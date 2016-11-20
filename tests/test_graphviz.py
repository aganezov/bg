import collections
import unittest

try:
    from unittest.mock import *
except ImportError:
    from mock import *

from ete3 import TreeNode

from bg.breakpoint_graph import BreakpointGraph
from bg.breakpoint_graph import CompleteMultiEdgeConnectedComponentFilter
from bg.edge import BGEdge
from bg.genome import BGGenome
from bg.graphviz import BGVertexShapeProcessor, BGVertexTextProcessor, BGVertexProcessor, BGEdgeShapeProcessor, BGEdgeProcessor, \
    BGEdgeTextProcessor, \
    BreakpointGraphProcessor, LabelFormat, Colors, BGTreeVertexShapeProcessor, BGTreeVertexTextProcessor, BGTreeVertexProcessor, \
    BGTreeEdgeShapeProcessor, \
    BGTreeEdgeTextProcessor, BGTreeEdgeProcessor, ShapeProcessor, TextProcessor, ColorSource, BGTreeProcessor
from bg.multicolor import Multicolor
from bg.tree import BGTree
from bg.utils import add_to_dict_with_path
from bg.vertices import TaggedBlockVertex, TaggedInfinityVertex, BlockVertex, InfinityVertex


class BGVertexShapeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultVertexShapeProcessor = BGVertexShapeProcessor()

    def test_default_shape(self):
        self.assertEqual("oval", self.defaultVertexShapeProcessor.get_shape())

    def test_default_shape_for_regular_non_bg_vertex(self):
        for vertex in [1, "1", (1,), Mock(spec=collections.Hashable), Mock(spec=TaggedBlockVertex)]:
            self.assertEqual("oval", self.defaultVertexShapeProcessor.get_shape(vertex))

    def test_default_shape_for_regular_bg_vertex(self):
        self.assertEqual("oval", self.defaultVertexShapeProcessor.get_shape(entry=BlockVertex(name="test")))

    def test_default_shape_for_irregular_bg_vertex(self):
        self.assertEqual("point", self.defaultVertexShapeProcessor.get_shape(entry=InfinityVertex(name="test")))

    def test_shape_attrib_template(self):
        self.assertEqual("shape=\"{shape}\"", self.defaultVertexShapeProcessor.shape_attrib_template)

    def test_default_pen_width(self):
        self.assertEqual(1, self.defaultVertexShapeProcessor.get_pen_width())

    def test_pen_width_attrib_template(self):
        self.assertEqual("penwidth=\"{pen_width}\"", self.defaultVertexShapeProcessor.pen_width_attrib_template)

    def test_get_all_attributes_as_list_of_strings_regular_vertex(self):
        vertex = TaggedBlockVertex("10t")
        self.assertSetEqual({"shape=\"oval\"", "penwidth=\"1\""},
                            set(self.defaultVertexShapeProcessor.get_attributes_string_list(entry=vertex)))

    def test_get_all_attributes_as_list_of_strings_irregular_vertex(self):
        vertex = TaggedInfinityVertex("10t")
        self.assertSetEqual({"shape=\"point\"", "penwidth=\"1\""},
                            set(self.defaultVertexShapeProcessor.get_attributes_string_list(entry=vertex)))


class BGVertexTextProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultVertexTextProcessor = BGVertexTextProcessor()

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
        self.assertEqual("\"namet\"", self.defaultVertexTextProcessor.get_text(entry=regular_vertex))
        self.assertEqual("\"namet\"", self.defaultVertexTextProcessor.get_text(entry=regular_vertex, label_format="plain"))
        self.assertEqual("\"namet\"",
                         self.defaultVertexTextProcessor.get_text(entry=regular_vertex,
                                                                  label_format=LabelFormat.plain))

    def test_vertex_name_html_text(self):
        regular_vertex = TaggedBlockVertex(name="namet")
        self.assertEqual("<name<SUP>t</SUP>>", self.defaultVertexTextProcessor.get_text(entry=regular_vertex, label_format="html"))
        self.assertEqual("<name<SUP>t</SUP>>",
                         self.defaultVertexTextProcessor.get_text(entry=regular_vertex,
                                                                  label_format=LabelFormat.html))
        self.assertEqual("<namet>",
                         self.defaultVertexTextProcessor.get_text(entry="namet", label_format=LabelFormat.html))

    def test_tagged_vertex_name_plain(self):
        tagged_vertex = TaggedBlockVertex(name="namet")
        tagged_vertex.add_tag("tag1", 10)
        tagged_vertex.add_tag("tag2", 20)
        self.assertEqual("\"namet\n(tag1:10)\n(tag2:20)\"", self.defaultVertexTextProcessor.get_text(entry=tagged_vertex))
        self.assertEqual("\"namet\n(tag1:10)\n(tag2:20)\"",
                         self.defaultVertexTextProcessor.get_text(entry=tagged_vertex, label_format="plain"))

    def test_tagged_vertex_name_html(self):
        tagged_vertex = TaggedBlockVertex(name="namet")
        tagged_vertex.add_tag("tag1", 10)
        tagged_vertex.add_tag("tag2", 20)
        self.assertEqual("<name<SUP>t</SUP>\n(tag1:10)\n(tag2:20)>",
                         self.defaultVertexTextProcessor.get_text(entry=tagged_vertex, label_format="html"))

    def test_get_all_attributes_as_list_of_strings_regular_vertex(self):
        vertex = TaggedBlockVertex("10t")
        self.assertSetEqual({"label=\"10t\"", "fontname=\"Arial\"", "fontsize=\"12\"", "fontcolor=\"black\""},
                            set(self.defaultVertexTextProcessor.get_attributes_string_list(entry=vertex)))
        self.assertSetEqual({"label=\"10t\"", "fontname=\"Arial\"", "fontsize=\"12\"", "fontcolor=\"black\""},
                            set(self.defaultVertexTextProcessor.get_attributes_string_list(entry=vertex, label_format="plain")))


class BGVertexProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultVertexProcessor = BGVertexProcessor()

    def test_default_vertex_shape_processor_field(self):
        self.assertIsInstance(self.defaultVertexProcessor.shape_processor, BGVertexShapeProcessor)

    def test_default_vertex_text_processor(self):
        self.assertIsInstance(self.defaultVertexProcessor.text_processor, BGVertexTextProcessor)

    def test_overall_template(self):
        self.assertEqual("\"{v_id}\" [{attributes}];", self.defaultVertexProcessor.template)

    def test_getting_non_bg_vertex_id(self):
        vertex = "1"
        self.assertEqual(1, self.defaultVertexProcessor.get_vertex_id(vertex=vertex))
        self.assertEqual(1,
                         self.defaultVertexProcessor.get_vertex_id(vertex=vertex))  # consecutive access shall return previously assigned id
        self.assertEqual(1,
                         self.defaultVertexProcessor.get_vertex_id(vertex=vertex))  # consecutive access shall return previously assigned id

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

    def test_getting_irregular_bg_vertices_same_block_different_tags(self):
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
        self.assertEqual("\"1\" [label=\"10t\", fontname=\"Arial\", fontsize=\"12\", fontcolor=\"black\", shape=\"oval\", penwidth=\"1\"];",
                         self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex))
        self.assertEqual(
            "\"1\" [label=<10<SUP>t</SUP>>, fontname=\"Arial\", fontsize=\"12\", fontcolor=\"black\", shape=\"oval\", penwidth=\"1\"];",
            self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex, label_format="html"))

    def test_full_regular_vertex_with_tags_export_all_default(self):
        vertex = TaggedBlockVertex("10t")
        vertex.add_tag("tag1", 1)
        vertex.add_tag("tag2", 2)
        self.assertEqual(
            "\"1\" [label=\"10t\n(tag1:1)\n(tag2:2)\", fontname=\"Arial\", fontsize=\"12\", fontcolor=\"black\", shape=\"oval\", penwidth=\"1\"];",
            self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex))
        self.assertEqual(
            "\"1\" [label=<10<SUP>t</SUP>\n(tag1:1)\n(tag2:2)>, fontname=\"Arial\", fontsize=\"12\", fontcolor=\"black\", shape=\"oval\", penwidth=\"1\"];",
            self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex, label_format="html"))

    def test_full_irregular_vertex_graphviz_entry_all_default(self):
        vertex = TaggedInfinityVertex("10t")
        self.assertEqual("\"1\" [shape=\"point\", penwidth=\"1\"];", self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex))
        self.assertEqual("\"1\" [shape=\"point\", penwidth=\"1\"];",
                         self.defaultVertexProcessor.export_vertex_as_dot(vertex=vertex, label_format="html"))


class BGEdgeShapeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultEdgeShapeProcessor = BGEdgeShapeProcessor()
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
        self.assertEqual("style=\"{style}\"", self.defaultEdgeShapeProcessor.style_attrib_template)

    def test_default_pen_width(self):
        self.assertEqual(1, self.defaultEdgeShapeProcessor.get_pen_width())

    def test_pen_width_attribute_template(self):
        self.assertEqual("penwidth=\"{pen_width}\"", self.defaultEdgeShapeProcessor.pen_width_attrib_template)

    def test_default_regular_edge_pen_width(self):
        self.assertEqual(1, self.defaultEdgeShapeProcessor.get_pen_width(self.edge))

    def test_default_irregular_edge_pen_width(self):
        self.assertEqual(.7, self.defaultEdgeShapeProcessor.get_pen_width(self.ir_edge))

    def test_default_repeat_edge_pen_width(self):
        self.assertEqual(.7, self.defaultEdgeShapeProcessor.get_pen_width(self.r_edge))

    def test_get_dot_colors_for_multicolor_single_color(self):
        mc = Multicolor(BGGenome("genome1"))
        dot_colors = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc)
        self.assertEqual(len(dot_colors), 1)
        self.assertEqual(len(set(dot_colors)), 1)
        dot_color = dot_colors[0]
        self.assertIn(dot_color, Colors)
        mc2 = Multicolor(BGGenome("genome1"))
        dot_colors2 = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc2)
        self.assertListEqual(dot_colors, dot_colors2)

    def test_get_dot_colors_for_multicolor_multiple_colors(self):
        mc = Multicolor(BGGenome("genome1"), BGGenome("genome2"), BGGenome("genome3"))
        dot_colors = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc)
        self.assertEqual(len(dot_colors), 3)
        self.assertEqual(len(set(dot_colors)), 3)
        for dot_color in dot_colors:
            self.assertIn(dot_color, Colors)
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
        self.assertIn(dot_color, Colors)
        mc2 = Multicolor(BGGenome("genome1"), BGGenome("genome1"))
        dot_colors2 = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc2)
        self.assertEqual(len(dot_colors2), 2)
        self.assertEqual(len(set(dot_colors2)), 1)
        self.assertSetEqual(set(dot_colors2), set(dot_colors))

    def test_get_dot_colors_for_multicolor_multiple_colors_with_greater_multiplicity(self):
        mc = Multicolor(BGGenome("genome1"), BGGenome("genome1"), BGGenome("genome1"), BGGenome("genome2"), BGGenome("genome2"),
                        BGGenome("genome3"))
        dot_colors = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=mc)
        self.assertEqual(len(dot_colors), 6)
        self.assertEqual(len(set(dot_colors)), 3)
        for color in dot_colors:
            self.assertIn(color, Colors)
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
        self.assertEqual("color=\"{color}\"", self.defaultEdgeShapeProcessor.color_attrib_template)

    def test_get_all_attributes_as_list_of_strings_regular_edge(self):
        color = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=Multicolor(self.color1))[0]
        self.assertSetEqual({"color=\"" + color.value + "\"", "style=\"solid\"", "penwidth=\"1\""},
                            set(self.defaultEdgeShapeProcessor.get_attributes_string_list(entry=self.edge)))

    def test_get_all_attributes_as_list_of_strings_irregular_edge(self):
        color = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=Multicolor(self.color1))[0]
        self.assertSetEqual({"color=\"" + color.value + "\"", "style=\"dotted\"", "penwidth=\"0.7\""},
                            set(self.defaultEdgeShapeProcessor.get_attributes_string_list(entry=self.ir_edge)))

    def test_get_all_attributes_as_list_of_strings_repeat_edge(self):
        color = self.defaultEdgeShapeProcessor.get_dot_colors(multicolor=Multicolor(self.color1))[0]
        self.assertSetEqual({"color=\"" + color.value + "\"", "style=\"dashed\"", "penwidth=\"0.7\""},
                            set(self.defaultEdgeShapeProcessor.get_attributes_string_list(entry=self.r_edge)))

    def test_get_all_attribute_as_list_of_strings_multiedge_error(self):
        with self.assertRaises(ValueError):
            multiedge = BGEdge(vertex1=self.regular_vertex, vertex2=self.regular_vertex2, multicolor=Multicolor(self.color1, self.color2))
            self.defaultEdgeShapeProcessor.get_attributes_string_list(entry=multiedge)
        with self.assertRaises(ValueError):
            multiedge = BGEdge(vertex1=self.regular_vertex, vertex2=self.regular_vertex2, multicolor=Multicolor(self.color1, self.color1))
            self.defaultEdgeShapeProcessor.get_attributes_string_list(entry=multiedge)


class BGEdgeTextProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.defaultEdgeTextProcessor = BGEdgeTextProcessor()
        self.regular_edge = BGEdge(vertex1=TaggedBlockVertex("10t"), vertex2=TaggedBlockVertex("11h"), multicolor=Multicolor())
        self.irregular_edge = BGEdge(vertex1=TaggedInfinityVertex("11h"), vertex2=TaggedBlockVertex("11h"), multicolor=Multicolor())
        repeat_irregular_vertex = TaggedInfinityVertex("11h")
        repeat_irregular_vertex.add_tag("repeat", "LLC1h")
        self.irregular_repeat_edge = BGEdge(vertex1=repeat_irregular_vertex, vertex2=TaggedBlockVertex("11h"), multicolor=Multicolor())

    def test_default_label_size(self):
        self.assertEqual(7, self.defaultEdgeTextProcessor.get_text_size(entry=self.regular_edge))
        self.assertEqual(7, self.defaultEdgeTextProcessor.get_text_size(entry=self.irregular_edge))
        self.assertEqual(7, self.defaultEdgeTextProcessor.get_text_size(entry=self.irregular_repeat_edge))

    def test_default_font(self):
        self.assertEqual("Arial", self.defaultEdgeTextProcessor.get_text_font(entry=self.regular_edge))
        self.assertEqual("Arial", self.defaultEdgeTextProcessor.get_text_font(entry=self.irregular_edge))
        self.assertEqual("Arial", self.defaultEdgeTextProcessor.get_text_font(entry=self.irregular_repeat_edge))

    def test_default_color(self):
        self.assertEqual("black", self.defaultEdgeTextProcessor.get_text_color(entry=self.regular_edge))
        self.assertEqual("black", self.defaultEdgeTextProcessor.get_text_color(entry=self.irregular_edge))
        self.assertEqual("black", self.defaultEdgeTextProcessor.get_text_color(entry=self.irregular_repeat_edge))

    def test_text_size_template(self):
        self.assertEqual("fontsize=\"{size}\"", self.defaultEdgeTextProcessor.size_attrib_template)

    def test_text_font_template(self):
        self.assertEqual("fontname=\"{font}\"", self.defaultEdgeTextProcessor.font_attrib_template)

    def test_text_color_template(self):
        self.assertEqual("fontcolor=\"{color}\"", self.defaultEdgeTextProcessor.color_attrib_template)

    def test_label_attrib_template(self):
        self.assertEqual("label={label}", self.defaultEdgeTextProcessor.label_attrib_template)

    def test_get_label_regular_edge_plain(self):
        self.assertEqual("\"\"", self.defaultEdgeTextProcessor.get_text(entry=self.regular_edge))
        self.assertEqual("\"\"", self.defaultEdgeTextProcessor.get_text(entry=self.regular_edge, label_format="plain"))

    def test_get_label_regular_edge_html(self):
        self.assertEqual("<>", self.defaultEdgeTextProcessor.get_text(entry=self.regular_edge, label_format="html"))

    def test_get_label_irregular_edge_plain(self):
        self.assertEqual("\"\"", self.defaultEdgeTextProcessor.get_text(entry=self.irregular_edge))
        self.assertEqual("\"\"", self.defaultEdgeTextProcessor.get_text(entry=self.irregular_edge, label_format="plain"))

    def test_get_label_irregular_edge_html(self):
        self.assertEqual("<>", self.defaultEdgeTextProcessor.get_text(entry=self.irregular_edge, label_format="html"))

    def test_get_label_irregular_repeat_edge_plain(self):
        self.assertEqual("\"r:LLC1h\"", self.defaultEdgeTextProcessor.get_text(entry=self.irregular_repeat_edge))
        self.assertEqual("\"r:LLC1h\"", self.defaultEdgeTextProcessor.get_text(entry=self.irregular_repeat_edge, label_format="plain"))

    def test_get_label_irregular_repeat_edge_html(self):
        self.assertEqual("<r:LLC1<SUP>h</SUP>>",
                         self.defaultEdgeTextProcessor.get_text(entry=self.irregular_repeat_edge, label_format="html"))

    def test_get_attributes_as_string_list_regular_edge(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.regular_edge)))
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.regular_edge, label_format="plain")))

    def test_get_attributes_as_string_list_regular_edge_html(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=<>"},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.regular_edge, label_format="html")))

    def test_get_attributes_irregular_repeat_edge_with_attributes_in_edges_data(self):
        add_to_dict_with_path(destination_dict=self.irregular_repeat_edge.data,
                              path=["dir1", "dir2"], key="important", value="to_display")
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"important:to_display\nr:LLC1h\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.irregular_repeat_edge,
                                                                                         label_format="plain",
                                                                                         edge_attributes_to_be_displayed=[
                                                                                             (["dir1", "dir2"], "important")])))

    def test_get_attributes_as_string_list_irregular_edge(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.irregular_edge)))
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.regular_edge, label_format="plain")))

    def test_get_attributes_as_string_list_irregular_edge_html(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=<>"},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.regular_edge, label_format="html")))

    def test_get_attributes_as_string_list_repeat_edge(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"r:LLC1h\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.irregular_repeat_edge)))
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=\"r:LLC1h\""},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.irregular_repeat_edge,
                                                                                         label_format="plain")))

    def test_get_attributes_as_string_list_repeat_edge_html(self):
        self.assertSetEqual({"fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\"", "label=<r:LLC1<SUP>h</SUP>>"},
                            set(self.defaultEdgeTextProcessor.get_attributes_string_list(entry=self.irregular_repeat_edge,
                                                                                         label_format="html")))


class BGEdgeProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.vertex_processor = BGVertexProcessor()
        self.defaultEdgeProcessor = BGEdgeProcessor(vertex_processor=self.vertex_processor)
        self.regular_vertex = TaggedBlockVertex(1)
        self.regular_vertex2 = TaggedBlockVertex(2)
        self.color1 = BGGenome("genome1")
        self.color2 = BGGenome("genome2")
        self.color3 = BGGenome("genome3")
        self.edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.regular_vertex2, multicolor=Multicolor(self.color1))
        self.irregular_vertex = InfinityVertex("v1")
        self.ir_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.irregular_vertex, multicolor=Multicolor(self.color1))
        self.repeat_vertex = TaggedInfinityVertex("v1")
        self.repeat_vertex.add_tag("repeat", "LLC1h")
        self.r_edge = BGEdge(vertex1=self.regular_vertex, vertex2=self.repeat_vertex, multicolor=Multicolor(self.color1))
        self.repeat_vertex2 = TaggedInfinityVertex("v1")
        self.repeat_vertex2.add_tag("repeat", "LLC2h")
        self.r_edge2 = BGEdge(vertex1=self.regular_vertex, vertex2=self.repeat_vertex2, multicolor=Multicolor(self.color1))

    def test_edge_shape_processor_field(self):
        self.assertIsInstance(self.defaultEdgeProcessor.shape_processor, BGEdgeShapeProcessor)

    def test_edge_text_processor_field(self):
        self.assertIsInstance(self.defaultEdgeProcessor.text_processor, BGEdgeTextProcessor)

    def test_overall_template(self):
        self.assertEqual("\"{v1_id}\" -- \"{v2_id}\" [{attributes}];", self.defaultEdgeProcessor.template)

    def test_regular_edge_graphviz_export_entries_single_colored_no_multiplicity(self):
        v1_id = self.vertex_processor.get_vertex_id(self.edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.edge.vertex2)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=self.edge.multicolor)[0].value
        expected_entry = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + str_color1 + "\", style=\"solid\", penwidth=\"1\"];"
        graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.edge)
        self.assertIsInstance(graphviz_entries, list)
        for entry in graphviz_entries:
            self.assertIsInstance(entry, str)
        self.assertEqual(len(graphviz_entries), 1)
        self.assertEqual(graphviz_entries[0], expected_entry)

    def test_regular_edge_graphviz_export_entries_multi_colored_no_multiplicity(self):
        v1_id = self.vertex_processor.get_vertex_id(self.edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.edge.vertex2)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color1))[0].value
        str_color2 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color2))[0].value
        expected_entry_1 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"solid\", penwidth=\"1\"];"
        expected_entry_2 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color2 + "\", style=\"solid\", penwidth=\"1\"];"
        self.edge.multicolor = Multicolor(self.color1, self.color2)
        graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.edge)
        self.assertIsInstance(graphviz_entries, list)
        self.assertEqual(len(graphviz_entries), 2)
        for entry in graphviz_entries:
            self.assertIsInstance(entry, str)
            self.assertIn(entry, [expected_entry_1, expected_entry_2])

    def test_regular_edge_graphviz_export_entries_single_colored_with_multiplicity(self):
        v1_id = self.vertex_processor.get_vertex_id(self.edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.edge.vertex2)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=self.edge.multicolor)[0].value
        expected_entry = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + str_color1 + "\", style=\"solid\", penwidth=\"1\"];"
        self.edge.multicolor = Multicolor(self.color1, self.color1, self.color1)
        graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.edge)
        self.assertIsInstance(graphviz_entries, list)
        for entry in graphviz_entries:
            self.assertIsInstance(entry, str)
            self.assertEqual(entry, expected_entry)
        self.assertEqual(len(graphviz_entries), 3)

    def test_regular_edge_graphviz_export_entries_multi_colored_with_multiplicity(self):
        v1_id = self.vertex_processor.get_vertex_id(self.edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.edge.vertex2)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color1))[0].value
        str_color2 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color2))[0].value
        str_color3 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color3))[0].value
        expected_entry_1 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"solid\", penwidth=\"1\"];"
        expected_entry_2 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color2 + "\", style=\"solid\", penwidth=\"1\"];"
        expected_entry_3 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color3 + "\", style=\"solid\", penwidth=\"1\"];"
        self.edge.multicolor = Multicolor(self.color1, self.color2, self.color1, self.color1, self.color2, self.color3)
        graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.edge)
        self.assertIsInstance(graphviz_entries, list)
        self.assertEqual(len(graphviz_entries), 6)
        for entry in graphviz_entries:
            self.assertIsInstance(entry, str)
            self.assertIn(entry, [expected_entry_1, expected_entry_2, expected_entry_3])

    def test_irregular_edge_graphviz_export_entries_single_colored_no_multiplicity(self):
        v1_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex2)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=self.ir_edge.multicolor)[0].value
        expected_entry = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.ir_edge)
        self.assertIsInstance(graphviz_entries, list)
        for entry in graphviz_entries:
            self.assertIsInstance(entry, str)
        self.assertEqual(len(graphviz_entries), 1)
        self.assertEqual(graphviz_entries[0], expected_entry)

    def test_irregular_edge_graphviz_export_entries_multi_colored_no_multiplicity(self):
        v1_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex2)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color1))[0].value
        str_color2 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color2))[0].value
        self.ir_edge.multicolor = Multicolor(self.color1, self.color2)
        expected_entry1 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        expected_entry2 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color2 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.ir_edge)
        self.assertIsInstance(graphviz_entries, list)
        for entry in graphviz_entries:
            self.assertIsInstance(entry, str)
            self.assertIn(entry, [expected_entry1, expected_entry2])
        self.assertEqual(len(graphviz_entries), 2)
        self.assertEqual(len(set(graphviz_entries)), 2)

    def test_irregular_edge_graphviz_export_entries_single_colored_with_multiplicity(self):
        v1_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex2)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color1))[0].value
        expected_entry = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        self.ir_edge.multicolor = Multicolor(self.color1, self.color1, self.color1)
        graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.ir_edge)
        self.assertIsInstance(graphviz_entries, list)
        for entry in graphviz_entries:
            self.assertIsInstance(entry, str)
            self.assertEqual(entry, expected_entry)
        self.assertEqual(len(graphviz_entries), 3)
        self.assertEqual(len(set(graphviz_entries)), 1)

    def test_irregular_edge_graphviz_export_entries_multi_colored_with_multiplicity(self):
        v1_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex2)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color1))[0].value
        str_color2 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color2))[0].value
        str_color3 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color3))[0].value
        self.ir_edge.multicolor = Multicolor(self.color1, self.color1, self.color1, self.color2, self.color2, self.color3)
        expected_entry1 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        expected_entry2 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color2 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        expected_entry3 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color3 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.ir_edge)
        self.assertIsInstance(graphviz_entries, list)
        for entry in graphviz_entries:
            self.assertIsInstance(entry, str)
            self.assertIn(entry, [expected_entry1, expected_entry2, expected_entry3])
        self.assertEqual(len(graphviz_entries), 6)
        self.assertEqual(len(set(graphviz_entries)), 3)

    def test_repeat_edge_graphviz_export_entries_joined_with_irregular_edge_single_colored(self):
        v1_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex2)
        v3_id = self.vertex_processor.get_vertex_id(self.r_edge.vertex1)
        v4_id = self.vertex_processor.get_vertex_id(self.r_edge.vertex2)
        self.assertEqual(v1_id, v3_id)
        self.assertEqual(v2_id, v4_id)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color1))[0].value
        expected_entry1 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        expected_entry2_plain = "\"" + str(v3_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dashed\", penwidth=\"0.7\", label=\"r:LLC1h\", fontname=\"Arial\", fontsize=\"7\", fontcolor=\"black\"];"
        expected_entry2_html = "\"" + str(v3_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dashed\", penwidth=\"0.7\", label=<r:LLC1<SUP>h</SUP>>, fontname=\"Arial\", fontsize=\"7\", fontcolor=\"black\"];"
        ir_edge_graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.ir_edge)
        r_edge_graphviz_entries_plain = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.r_edge)
        r_edge_graphviz_entries_html = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.r_edge, label_format="html")
        for export_entry in [ir_edge_graphviz_entries, r_edge_graphviz_entries_plain, r_edge_graphviz_entries_html]:
            self.assertIsInstance(export_entry, list)
            self.assertEqual(len(export_entry), 1)
        self.assertEqual(ir_edge_graphviz_entries[0], expected_entry1)
        self.assertEqual(r_edge_graphviz_entries_plain[0], expected_entry2_plain)
        self.assertEqual(r_edge_graphviz_entries_html[0], expected_entry2_html)

    def test_repeat_edge_graphviz_export_entries_joined_with_other_repeat_edges_ad_irregular_edges_multi_colored(self):
        v1_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(self.ir_edge.vertex2)
        v3_id = self.vertex_processor.get_vertex_id(self.r_edge.vertex1)
        v4_id = self.vertex_processor.get_vertex_id(self.r_edge.vertex2)
        v5_id = self.vertex_processor.get_vertex_id(self.r_edge2.vertex1)
        v6_id = self.vertex_processor.get_vertex_id(self.r_edge2.vertex2)
        self.assertEqual(v1_id, v3_id)
        self.assertEqual(v3_id, v5_id)
        self.assertEqual(v2_id, v4_id)
        self.assertEqual(v4_id, v6_id)
        mc1 = Multicolor(self.color1, self.color1)
        mc2 = Multicolor(self.color1, self.color2)
        mc3 = Multicolor(self.color1, self.color2, self.color3, self.color3)
        str_color1 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color1))[0].value
        str_color2 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color2))[0].value
        str_color3 = self.defaultEdgeProcessor.shape_processor.get_dot_colors(multicolor=Multicolor(self.color3))[0].value
        ie_expected_entry1 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        ie_expected_entry2 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color2 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        ie_expected_entry3 = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color3 + "\", style=\"dotted\", penwidth=\"0.7\"];"
        re1_expected_entry1_plain = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dashed\", penwidth=\"0.7\", label=\"r:LLC1h\", fontname=\"Arial\", fontsize=\"7\", fontcolor=\"black\"];"
        re1_expected_entry1_html = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dashed\", penwidth=\"0.7\", label=<r:LLC1<SUP>h</SUP>>, fontname=\"Arial\", fontsize=\"7\", fontcolor=\"black\"];"
        re2_expected_entry1_plain = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dashed\", penwidth=\"0.7\", label=\"r:LLC2h\", fontname=\"Arial\", fontsize=\"7\", fontcolor=\"black\"];"
        re2_expected_entry1_html = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color1 + "\", style=\"dashed\", penwidth=\"0.7\", label=<r:LLC2<SUP>h</SUP>>, fontname=\"Arial\", fontsize=\"7\", fontcolor=\"black\"];"
        re2_expected_entry2_plain = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color2 + "\", style=\"dashed\", penwidth=\"0.7\", label=\"r:LLC2h\", fontname=\"Arial\", fontsize=\"7\", fontcolor=\"black\"];"
        re2_expected_entry2_html = "\"" + str(v1_id) + "\" -- \"" + str(
            v2_id) + "\" [color=\"" + str_color2 + "\", style=\"dashed\", penwidth=\"0.7\", label=<r:LLC2<SUP>h</SUP>>, fontname=\"Arial\", fontsize=\"7\", fontcolor=\"black\"];"
        self.ir_edge.multicolor = mc3
        self.r_edge.multicolor = mc1
        self.r_edge2.multicolor = mc2
        ie_graphviz_entries = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.ir_edge)
        re1_graphviz_entries_plain = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.r_edge)
        re1_graphviz_entries_html = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.r_edge, label_format="html")
        re2_graphviz_entries_plain = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.r_edge2)
        re2_graphviz_entries_html = self.defaultEdgeProcessor.export_edge_as_dot(edge=self.r_edge2, label_format="html")
        self.assertIsInstance(ie_graphviz_entries, list)
        self.assertEqual(len(ie_graphviz_entries), 4)
        self.assertEqual(len(set(ie_graphviz_entries)), 3)
        for entry in ie_graphviz_entries:
            self.assertIn(entry, [ie_expected_entry1, ie_expected_entry2, ie_expected_entry3])
        self.assertIsInstance(re1_graphviz_entries_plain, list)
        self.assertIsInstance(re1_graphviz_entries_html, list)
        self.assertEqual(len(re1_graphviz_entries_plain), 2)
        self.assertEqual(len(set(re1_graphviz_entries_plain)), 1)
        self.assertEqual(len(re1_graphviz_entries_html), 2)
        self.assertEqual(len(set(re1_graphviz_entries_html)), 1)
        for entry in re1_graphviz_entries_plain:
            self.assertEqual(entry, re1_expected_entry1_plain)
        for entry in re1_graphviz_entries_html:
            self.assertEqual(entry, re1_expected_entry1_html)
        self.assertIsInstance(re2_graphviz_entries_plain, list)
        self.assertIsInstance(re2_graphviz_entries_html, list)
        self.assertEqual(len(re2_graphviz_entries_plain), 2)
        self.assertEqual(len(set(re2_graphviz_entries_plain)), 2)
        self.assertEqual(len(re2_graphviz_entries_html), 2)
        self.assertEqual(len(set(re2_graphviz_entries_html)), 2)
        for entry in re2_graphviz_entries_plain:
            self.assertIn(entry, [re2_expected_entry1_plain, re2_expected_entry2_plain])
        for entry in re2_graphviz_entries_html:
            self.assertIn(entry, [re2_expected_entry1_html, re2_expected_entry2_html])


class BreakpointGraphProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.vertex_processor = BGVertexProcessor()
        self.edge_processor = BGEdgeProcessor(vertex_processor=self.vertex_processor)
        self.defaultGraphProcessor = BreakpointGraphProcessor(vertex_processor=self.vertex_processor, edge_processor=self.edge_processor)
        self.v1 = TaggedBlockVertex("10h")
        self.v2 = TaggedBlockVertex("10t")
        self.v3 = TaggedBlockVertex("11t")
        self.v4 = TaggedBlockVertex("11h")
        self.i_v1 = TaggedInfinityVertex("10h")
        self.i_v2 = TaggedInfinityVertex("10t")
        self.i_v3 = TaggedInfinityVertex("11t")
        self.i_v4 = TaggedInfinityVertex("11h")
        self.color1 = BGGenome("genome1")
        self.color2 = BGGenome("genome2")
        self.color3 = BGGenome("genome3")
        self.mc1 = Multicolor(self.color1)
        self.mc2 = Multicolor(self.color1, self.color2)
        self.mc3 = Multicolor(self.color1, self.color2, self.color3)
        self.edge1 = BGEdge(vertex1=self.v1, vertex2=self.v2, multicolor=self.mc1)
        self.edge2 = BGEdge(vertex1=self.v1, vertex2=self.v3, multicolor=self.mc2)
        self.edge3 = BGEdge(vertex1=self.v3, vertex2=self.v4, multicolor=self.mc1)
        self.iedge1 = BGEdge(vertex1=self.v1, vertex2=self.i_v1, multicolor=self.mc2)
        self.iedge2 = BGEdge(vertex1=self.v2, vertex2=self.i_v2, multicolor=self.mc2)
        self.iedge3 = BGEdge(vertex1=self.v3, vertex2=self.i_v3, multicolor=self.mc1)
        self.iedge4 = BGEdge(vertex1=self.v4, vertex2=self.i_v4, multicolor=self.mc3)
        self.graph = BreakpointGraph()
        self.graph.add_bgedge(bgedge=self.edge1, merge=False)
        self.graph.add_bgedge(bgedge=self.edge2, merge=False)
        self.graph.add_bgedge(bgedge=self.edge3, merge=False)
        self.graph.add_bgedge(bgedge=self.iedge1, merge=False)
        self.graph.add_bgedge(bgedge=self.iedge2, merge=False)
        self.graph.add_bgedge(bgedge=self.iedge3, merge=False)
        self.graph.add_bgedge(bgedge=self.iedge4, merge=False)

    def test_overall_template(self):
        self.assertEqual("graph {{\n"
                         "{edges}\n"
                         "{vertices}\n"
                         "}}", self.defaultGraphProcessor.template)

    def test_cc_filters_field(self):
        self.assertIsInstance(self.defaultGraphProcessor.cc_filters, list)
        self.assertEqual(len(self.defaultGraphProcessor.cc_filters), 0)

    def test_cc_filter_template(self):
        self.assertEqual("{filter_name}: {filtered_cnt}", self.defaultGraphProcessor.cc_filter_template)

    def test_overall_cc_filters_template(self):
        self.assertEqual(
            "\"cc_filters\" [shape=\"square\", penwidth=\"5\", fontname=\"Arial\", fontsize=\"15\", label=\"{overall_filters_info}\"];",
            self.defaultGraphProcessor.cc_filters_template)

    def test_get_vertices_graphviz_entries_plain(self):
        vertices_entries = self.defaultGraphProcessor.export_vertices_as_dot(graph=self.graph)
        expected = [self.vertex_processor.export_vertex_as_dot(vertex=v) for v in
                    [self.v1, self.v2, self.v3, self.v4, self.i_v1, self.i_v2, self.i_v3, self.i_v4]]
        self.assertIsInstance(vertices_entries, list)
        self.assertEqual(len(vertices_entries), 8)
        for entry in vertices_entries:
            self.assertIsInstance(entry, str)
            self.assertIn(entry, expected)

    def test_get_vertices_graphviz_entries_html(self):
        vertices_entries = self.defaultGraphProcessor.export_vertices_as_dot(graph=self.graph, label_format="html")
        expected = [self.vertex_processor.export_vertex_as_dot(vertex=v, label_format="html") for v in
                    [self.v1, self.v2, self.v3, self.v4, self.i_v1, self.i_v2, self.i_v3, self.i_v4]]
        self.assertIsInstance(vertices_entries, list)
        self.assertEqual(len(vertices_entries), 8)
        for entry in vertices_entries:
            self.assertIsInstance(entry, str)
            self.assertIn(entry, expected)

    def test_get_edges_graphviz_entries_plain(self):
        edges_entries = self.defaultGraphProcessor.export_edges_as_dot(graph=self.graph)
        expected = [entry for e in [self.edge1, self.edge2, self.edge3, self.iedge1, self.iedge2, self.iedge3, self.iedge4] for edge in
                    [BGEdge(vertex1=e.vertex1, vertex2=e.vertex2, multicolor=e.multicolor),
                     BGEdge(vertex1=e.vertex2, vertex2=e.vertex1, multicolor=e.multicolor)] for entry in
                    self.edge_processor.export_edge_as_dot(edge=edge)]
        self.assertIsInstance(edges_entries, list)
        self.assertEqual(len(edges_entries), 12)
        for entry in edges_entries:
            self.assertIsInstance(entry, str)
            self.assertIn(entry, expected)

    def test_get_edges_graphviz_entries_html(self):
        edges_entries = self.defaultGraphProcessor.export_edges_as_dot(graph=self.graph)
        expected = [entry for e in [self.edge1, self.edge2, self.edge3, self.iedge1, self.iedge2, self.iedge3, self.iedge4] for edge in
                    [BGEdge(vertex1=e.vertex1, vertex2=e.vertex2, multicolor=e.multicolor),
                     BGEdge(vertex1=e.vertex2, vertex2=e.vertex1, multicolor=e.multicolor)] for entry in
                    self.edge_processor.export_edge_as_dot(edge=edge, label_format="html")]
        self.assertIsInstance(edges_entries, list)
        self.assertEqual(len(edges_entries), 12)
        for entry in edges_entries:
            self.assertIsInstance(entry, str)
            self.assertIn(entry, expected)

    def test_export_graph_as_dot_plain(self):
        graph = BreakpointGraph()
        bg_edge_v1 = BGEdge(vertex1=self.v1, vertex2=self.v2, multicolor=self.mc1)
        bg_edge_v2 = BGEdge(vertex1=self.v2, vertex2=self.v1, multicolor=self.mc1)
        graph.add_bgedge(bgedge=bg_edge_v1)
        expected_v1 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_v1)) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2) + "\n" + "}"
        expected_v2 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_v1)) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1) + "\n" + "}"
        expected_v3 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_v2)) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2) + "\n" + "}"
        expected_v4 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_v2)) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1) + "\n" + "}"
        graph_graphviz_entry = self.defaultGraphProcessor.export_graph_as_dot(graph=graph)
        self.assertIsInstance(graph_graphviz_entry, str)
        self.assertIn(graph_graphviz_entry, [expected_v1, expected_v2, expected_v3, expected_v4])

    def test_export_graph_as_dot_html(self):
        graph = BreakpointGraph()
        bg_edge_v1 = BGEdge(vertex1=self.v1, vertex2=self.v2, multicolor=self.mc1)
        bg_edge_v2 = BGEdge(vertex1=self.v2, vertex2=self.v1, multicolor=self.mc1)
        graph.add_bgedge(bgedge=bg_edge_v1)
        expected_v1 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_v1, label_format="html")) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1, label_format="html") + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2, label_format="html") + "\n" + "}"
        expected_v2 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_v1, label_format="html")) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2, label_format="html") + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1, label_format="html") + "\n" + "}"
        expected_v3 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_v2, label_format="html")) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1, label_format="html") + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2, label_format="html") + "\n" + "}"
        expected_v4 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_v2, label_format="html")) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2, label_format="html") + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1, label_format="html") + "\n" + "}"
        graph_graphviz_entry = self.defaultGraphProcessor.export_graph_as_dot(graph=graph, label_format="html")
        self.assertIsInstance(graph_graphviz_entry, str)
        self.assertIn(graph_graphviz_entry, [expected_v1, expected_v2, expected_v3, expected_v4])

    def test_export_graph_CME_cc_filter_as_dot_plain(self):
        graph = BreakpointGraph()
        bg_edge_1 = BGEdge(vertex1=self.v1, vertex2=self.v2, multicolor=self.mc1)
        bg_edge_1_r = BGEdge(vertex1=self.v2, vertex2=self.v1, multicolor=self.mc1)
        bg_edge_2 = BGEdge(vertex1=self.v3, vertex2=self.v4, multicolor=self.mc2)
        graph.add_bgedge(bgedge=bg_edge_1)
        graph.add_bgedge(bgedge=bg_edge_2)
        self.defaultGraphProcessor.cc_filters.append(CompleteMultiEdgeConnectedComponentFilter())
        expected_v1 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_1, label_format="html")) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1, label_format="html") + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2, label_format="html") + "\n" + \
                      "\"cc_filters\" [shape=\"square\", penwidth=\"5\", fontname=\"Arial\", fontsize=\"15\", label=\"Complete ME filter: 1\"];" + "\n" + \
                      "}"
        expected_v2 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_1, label_format="html")) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2, label_format="html") + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1, label_format="html") + "\n" + \
                      "\"cc_filters\" [shape=\"square\", penwidth=\"5\", fontname=\"Arial\", fontsize=\"15\", label=\"Complete ME filter: 1\"];" + "\n" + \
                      "}"
        expected_v3 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_1_r, label_format="html")) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1, label_format="html") + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2, label_format="html") + "\n" + \
                      "\"cc_filters\" [shape=\"square\", penwidth=\"5\", fontname=\"Arial\", fontsize=\"15\", label=\"Complete ME filter: 1\"];" + "\n" + \
                      "}"
        expected_v4 = "graph {\n" + \
                      "\n".join(self.edge_processor.export_edge_as_dot(edge=bg_edge_1_r, label_format="html")) + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v2, label_format="html") + "\n" + \
                      self.vertex_processor.export_vertex_as_dot(vertex=self.v1, label_format="html") + "\n" + \
                      "\"cc_filters\" [shape=\"square\", penwidth=\"5\", fontname=\"Arial\", fontsize=\"15\", label=\"Complete ME filter: 1\"];" + "\n" + \
                      "}"
        graph_graphviz_entry = self.defaultGraphProcessor.export_graph_as_dot(graph=graph, label_format="html")
        self.assertIsInstance(graph_graphviz_entry, str)
        self.assertIn(graph_graphviz_entry, [expected_v1, expected_v2, expected_v3, expected_v4])


class BGTreeTestCase(unittest.TestCase):
    def setUp(self):
        self.binary_tree = BGTree("((a, b), (c, (d, e)));")
        self.non_binary_tree = BGTree("((a, b, c), (d, e, (f, g, h)));")
        self.leaf_nodes_binary_tree = [node for node in self.binary_tree.nodes() if node.is_leaf()]
        self.leaf_nodes_binary_tree_sorted = sorted(self.leaf_nodes_binary_tree, key=lambda node: node.name)
        self.non_leaf_nodes_binary_tree = [node for node in self.binary_tree.nodes() if not node.is_leaf()]
        self.leaf_nodes_non_binary_tree = [node for node in self.non_binary_tree.nodes() if node.is_leaf()]
        self.non_leaf_nodes_non_binary_tree = [node for node in self.non_binary_tree.nodes() if not node.is_leaf()]
        self.leaf_branches_binary_tree = [edge for edge in self.binary_tree.edges() if
                                          isinstance(edge[0], BGGenome) or isinstance(edge[1], BGGenome)]
        self.non_leaf_branches_binary_tree = [edge for edge in self.binary_tree.edges() if
                                              not isinstance(edge[0], BGGenome) and not isinstance(edge[1], BGGenome)]
        self.leaf_branches_non_binary_tree = [edge for edge in self.non_binary_tree.edges() if
                                              isinstance(edge[0], BGGenome) or isinstance(edge[1], BGGenome)]
        self.non_leaf_branches_non_binary_tree = [edge for edge in self.non_binary_tree.edges() if
                                                  not isinstance(edge[0], BGGenome) and not isinstance(edge[1], BGGenome)]
        self.genome1 = BGGenome("a")
        self.genome2 = BGGenome("b")
        self.genome3 = BGGenome("c")
        self.genome4 = BGGenome("d")
        self.genome5 = BGGenome("e")
        self.sorted_genomes = [self.genome1, self.genome2, self.genome3, self.genome4, self.genome5]


class BGTreeVertexShapeProcessorTestCase(BGTreeTestCase):
    def setUp(self):
        super(BGTreeVertexShapeProcessorTestCase, self).setUp()
        self.default_tree_vertex_shape_processor = BGTreeVertexShapeProcessor()

    def test_shape_attrib_template(self):
        self.assertEqual("shape=\"{shape}\"", self.default_tree_vertex_shape_processor.shape_attrib_template)

    def test_color_attrib_template(self):
        self.assertEqual("color=\"{color}\"", self.default_tree_vertex_shape_processor.color_attrib_template)

    def test_style_attrib_template(self):
        self.assertEqual("style=\"{style}\"", self.default_tree_vertex_shape_processor.style_attrib_template)

    def test_penwidth_attrib_template(self):
        self.assertEqual("penwidth=\"{pen_width}\"", self.default_tree_vertex_shape_processor.pen_width_attrib_template)

    def test_get_shape_leaf_nodes(self):
        for node in self.leaf_nodes_binary_tree:
            self.assertEqual("oval", self.default_tree_vertex_shape_processor.get_shape(entry=node))
        for node in self.leaf_nodes_non_binary_tree:
            self.assertEqual("oval", self.default_tree_vertex_shape_processor.get_shape(entry=node))

    def test_get_shape_non_leaf_nodes(self):
        for node in self.non_leaf_nodes_binary_tree:
            self.assertEqual("oval", self.default_tree_vertex_shape_processor.get_shape(entry=node))
        for node in self.non_leaf_nodes_non_binary_tree:
            self.assertEqual("oval", self.default_tree_vertex_shape_processor.get_shape(entry=node))

    def test_get_pen_width_leaf_nodes(self):
        for node in self.leaf_nodes_binary_tree:
            self.assertEqual(3, self.default_tree_vertex_shape_processor.get_pen_width(entry=node))
        for node in self.leaf_nodes_non_binary_tree:
            self.assertEqual(3, self.default_tree_vertex_shape_processor.get_pen_width(entry=node))

    def test_get_pen_width_non_leaf_nodes(self):
        for node in self.non_leaf_nodes_binary_tree:
            self.assertEqual(1, self.default_tree_vertex_shape_processor.get_pen_width(entry=node))
        for node in self.non_leaf_nodes_non_binary_tree:
            self.assertEqual(1, self.default_tree_vertex_shape_processor.get_pen_width(entry=node))

    def test_get_style_leaf_nodes(self):
        for node in self.non_leaf_nodes_binary_tree:
            self.assertEqual("solid", self.default_tree_vertex_shape_processor.get_style(entry=node))
        for node in self.non_leaf_nodes_non_binary_tree:
            self.assertEqual("solid", self.default_tree_vertex_shape_processor.get_style(entry=node))

    def test_get_style_non_leaf_nodes(self):
        for node in self.non_leaf_nodes_binary_tree:
            self.assertEqual("solid", self.default_tree_vertex_shape_processor.get_style(entry=node))
        for node in self.non_leaf_nodes_non_binary_tree:
            self.assertEqual("solid", self.default_tree_vertex_shape_processor.get_style(entry=node))

    def test_get_color_no_color_source(self):
        leaf_nodes_colors = [self.default_tree_vertex_shape_processor.get_color_as_string(entry=node) for node in
                             self.leaf_nodes_binary_tree_sorted]
        genomes_colors = [self.default_tree_vertex_shape_processor.color_source.get_color_as_string(entry=genome) for genome in
                          self.sorted_genomes]
        for genome_color, node_color in zip(genomes_colors, leaf_nodes_colors):
            self.assertEqual(genome_color, node_color)
        non_leaf_nodes_colors = [self.default_tree_vertex_shape_processor.get_color_as_string(entry=node) for node in
                                 self.non_leaf_nodes_non_binary_tree]
        self.assertEqual(len(set(non_leaf_nodes_colors)), 1)
        for non_leaf_node_color in non_leaf_nodes_colors:
            self.assertNotIn(non_leaf_node_color, leaf_nodes_colors)
            self.assertNotIn(non_leaf_node_color, genomes_colors)

    def test_get_color_with_color_source(self):
        vsp = BGVertexShapeProcessor()
        genomes_colors = [vsp.get_color_as_string(genome) for genome in
                          [BGGenome("x"), BGGenome("y"), BGGenome("z")] + self.sorted_genomes]
        tree_vertex_shape_processor = BGTreeVertexShapeProcessor(color_source=vsp.color_source)
        leaf_colors = [tree_vertex_shape_processor.get_color_as_string(entry=node) for node in self.leaf_nodes_binary_tree_sorted]
        for genome_color, leaf_color in zip(genomes_colors[3:], leaf_colors):
            self.assertEqual(genome_color, leaf_color)
        non_leaf_nodes_colors = [tree_vertex_shape_processor.get_color_as_string(entry=node) for node in
                                 self.non_leaf_nodes_non_binary_tree]
        self.assertEqual(len(set(non_leaf_nodes_colors)), 1)
        for non_leaf_node_color in non_leaf_nodes_colors:
            self.assertNotIn(non_leaf_node_color, leaf_colors)
            self.assertNotIn(non_leaf_node_color, genomes_colors)

    def test_get_attributes_as_string_list(self):
        color_str = self.default_tree_vertex_shape_processor.get_color_as_string(entry=self.leaf_nodes_binary_tree[0])
        self.assertSetEqual({"shape=\"oval\"", "style=\"solid\"", "penwidth=\"3\"", "color=\"" + color_str + "\""},
                            set(self.default_tree_vertex_shape_processor.get_attributes_string_list(entry=self.leaf_nodes_binary_tree[0])))
        color_str2 = self.default_tree_vertex_shape_processor.get_color_as_string(entry=self.non_leaf_nodes_binary_tree[0])
        self.assertSetEqual({"shape=\"oval\"", "style=\"solid\"", "penwidth=\"1\"", "color=\"" + color_str2 + "\""},
                            set(self.default_tree_vertex_shape_processor.get_attributes_string_list(
                                entry=self.non_leaf_nodes_binary_tree[0])))


class BGTreeVertexTextProcessorTestCase(BGTreeTestCase):
    def setUp(self):
        super(BGTreeVertexTextProcessorTestCase, self).setUp()
        self.default_tree_vertex_text_processor = BGTreeVertexTextProcessor()

    def test_get_text_font_name_leaf_node(self):
        self.assertEqual("Arial", self.default_tree_vertex_text_processor.get_text_font(entry=self.leaf_nodes_binary_tree[0]))

    def test_get_text_font_name_non_leaf_node(self):
        self.assertEqual("Arial", self.default_tree_vertex_text_processor.get_text_font(entry=self.non_leaf_nodes_binary_tree[0]))

    def test_get_text_size_leaf_node(self):
        self.assertEqual(12, self.default_tree_vertex_text_processor.get_text_size(entry=self.leaf_nodes_binary_tree[0]))

    def test_get_text_size_non_leaf_node(self):
        self.assertEqual(12, self.default_tree_vertex_text_processor.get_text_size(entry=self.non_leaf_nodes_binary_tree[0]))

    def test_get_text_color_no_color_source(self):
        genome_colors = [self.default_tree_vertex_text_processor.color_source.get_color_as_string(entry=genome) for genome in
                         self.sorted_genomes]
        leaf_colors = [self.default_tree_vertex_text_processor.get_text_color(entry=node) for node in self.leaf_nodes_binary_tree_sorted]
        self.assertEqual(len(leaf_colors), 5)
        self.assertEqual(len(set(leaf_colors)), 5)
        for genome_color, node_color in zip(genome_colors, leaf_colors):
            self.assertEqual(genome_color, node_color)
        non_leaf_colors = [self.default_tree_vertex_text_processor.get_text_color(entry=node) for node in self.non_leaf_nodes_binary_tree]
        self.assertEqual(len(non_leaf_colors), 4)
        self.assertEqual(len(set(non_leaf_colors)), 1)
        for color in non_leaf_colors:
            self.assertNotIn(color, genome_colors)
            self.assertNotIn(color, leaf_colors)

    def test_get_text_color_with_color_source(self):
        vsp = BGVertexShapeProcessor()
        genome_colors = [vsp.get_color_as_string(genome) for genome in
                         [BGGenome("x"), BGGenome("y"), BGGenome("z")] + self.sorted_genomes]
        tree_vertex_text_processor = BGTreeVertexTextProcessor(color_source=vsp.color_source)
        leaf_colors = [tree_vertex_text_processor.get_text_color(entry=node) for node in self.leaf_nodes_binary_tree_sorted]
        self.assertEqual(len(leaf_colors), 5)
        self.assertEqual(len(set(leaf_colors)), 5)
        for node_color in leaf_colors:
            self.assertIn(node_color, genome_colors)
        non_leaf_colors = [tree_vertex_text_processor.get_text_color(entry=node) for node in self.non_leaf_nodes_binary_tree]
        self.assertEqual(len(non_leaf_colors), 4)
        self.assertEqual(len(set(non_leaf_colors)), 1)
        for color in non_leaf_colors:
            self.assertNotIn(color, genome_colors)
            self.assertNotIn(color, leaf_colors)

    def test_get_text_leaf_nodes_plain(self):
        self.assertEqual("\"a\"", self.default_tree_vertex_text_processor.get_text(entry=self.leaf_nodes_binary_tree_sorted[0]))
        self.assertEqual("\"a\"", self.default_tree_vertex_text_processor.get_text(entry=self.leaf_nodes_binary_tree_sorted[0],
                                                                                   label_format=LabelFormat.plain))

    def test_get_text_leaf_nodes_html(self):
        self.assertEqual("<a>", self.default_tree_vertex_text_processor.get_text(entry=self.leaf_nodes_binary_tree_sorted[0],
                                                                                 label_format="html"))
        self.assertEqual("<a>", self.default_tree_vertex_text_processor.get_text(entry=self.leaf_nodes_binary_tree_sorted[0],
                                                                                 label_format=LabelFormat.html))

    def test_get_text_non_leaf_node_plain(self):
        self.assertEqual("\"\"", self.default_tree_vertex_text_processor.get_text(entry=self.non_leaf_nodes_binary_tree[0]))
        self.assertEqual("\"\"", self.default_tree_vertex_text_processor.get_text(entry=self.non_leaf_nodes_binary_tree[0],
                                                                                  label_format=LabelFormat.plain))

    def test_get_text_non_leaf_node_html(self):
        self.assertEqual("<>", self.default_tree_vertex_text_processor.get_text(entry=self.non_leaf_nodes_binary_tree[0],
                                                                                label_format=LabelFormat.html))

    def test_get_attributes_string_list_leaf_node_plain(self):
        color1_str = self.default_tree_vertex_text_processor.get_text_color(entry=self.leaf_nodes_binary_tree_sorted[0])
        color2_str = self.default_tree_vertex_text_processor.get_text_color(entry=self.leaf_nodes_binary_tree_sorted[1])
        self.assertSetEqual({"fontcolor=\"" + color1_str + "\"", "fontsize=\"12\"", "fontname=\"Arial\"", "label=\"a\""},
                            set(self.default_tree_vertex_text_processor.get_attributes_string_list(
                                entry=self.leaf_nodes_binary_tree_sorted[0])))
        self.assertSetEqual({"fontcolor=\"" + color2_str + "\"", "fontsize=\"12\"", "fontname=\"Arial\"", "label=\"b\""},
                            set(self.default_tree_vertex_text_processor.get_attributes_string_list(
                                entry=self.leaf_nodes_binary_tree_sorted[1])))

    def test_get_attributes_string_list_leaf_node_html(self):
        color1_str = self.default_tree_vertex_text_processor.get_text_color(entry=self.leaf_nodes_binary_tree_sorted[0])
        color2_str = self.default_tree_vertex_text_processor.get_text_color(entry=self.leaf_nodes_binary_tree_sorted[1])
        self.assertSetEqual({"fontcolor=\"" + color1_str + "\"", "fontsize=\"12\"", "fontname=\"Arial\"", "label=<a>"},
                            set(self.default_tree_vertex_text_processor.get_attributes_string_list(
                                entry=self.leaf_nodes_binary_tree_sorted[0],
                                label_format=LabelFormat.html)))
        self.assertSetEqual({"fontcolor=\"" + color2_str + "\"", "fontsize=\"12\"", "fontname=\"Arial\"", "label=<b>"},
                            set(self.default_tree_vertex_text_processor.get_attributes_string_list(
                                entry=self.leaf_nodes_binary_tree_sorted[1],
                                label_format=LabelFormat.html)))

    def test_get_attributes_string_list_non_leaf_node_plain(self):
        color1_str = self.default_tree_vertex_text_processor.get_text_color(entry=self.non_leaf_nodes_non_binary_tree[0])
        color2_str = self.default_tree_vertex_text_processor.get_text_color(entry=self.non_leaf_nodes_binary_tree[1])
        self.assertSetEqual({"fontcolor=\"" + color1_str + "\"", "fontsize=\"12\"", "fontname=\"Arial\"", "label=\"\""},
                            set(self.default_tree_vertex_text_processor.get_attributes_string_list(
                                entry=self.non_leaf_nodes_binary_tree[0])))
        self.assertSetEqual({"fontcolor=\"" + color2_str + "\"", "fontsize=\"12\"", "fontname=\"Arial\"", "label=\"\""},
                            set(self.default_tree_vertex_text_processor.get_attributes_string_list(
                                entry=self.non_leaf_nodes_binary_tree[1])))

    def test_get_attributes_string_list_non_leaf_node_html(self):
        color1_str = self.default_tree_vertex_text_processor.get_text_color(entry=self.non_leaf_nodes_non_binary_tree[0])
        color2_str = self.default_tree_vertex_text_processor.get_text_color(entry=self.non_leaf_nodes_binary_tree[1])
        self.assertSetEqual({"fontcolor=\"" + color1_str + "\"", "fontsize=\"12\"", "fontname=\"Arial\"", "label=<>"},
                            set(self.default_tree_vertex_text_processor.get_attributes_string_list(entry=self.non_leaf_nodes_binary_tree[0],
                                                                                                   label_format=LabelFormat.html)))
        self.assertSetEqual({"fontcolor=\"" + color2_str + "\"", "fontsize=\"12\"", "fontname=\"Arial\"", "label=<>"},
                            set(self.default_tree_vertex_text_processor.get_attributes_string_list(entry=self.non_leaf_nodes_binary_tree[1],
                                                                                                   label_format=LabelFormat.html)))


class BGTreeVertexProcessorTestCase(BGTreeTestCase):
    def setUp(self):
        super(BGTreeVertexProcessorTestCase, self).setUp()
        self.default_tree_vertex_shape_processor = BGTreeVertexShapeProcessor()
        self.default_tree_vertex_text_processor = BGTreeVertexTextProcessor()
        self.default_tree_vertex_processor = BGTreeVertexProcessor(shape_processor=self.default_tree_vertex_shape_processor,
                                                                   text_processor=self.default_tree_vertex_text_processor)

    def test_overall_template(self):
        self.assertEqual("\"{v_id}\" [{attributes}];", self.default_tree_vertex_processor.template)

    def test_shape_processor_field(self):
        self.assertIs(self.default_tree_vertex_processor.shape_processor, self.default_tree_vertex_shape_processor)

    def test_text_processor_field(self):
        self.assertIs(self.default_tree_vertex_processor.text_processor, self.default_tree_vertex_text_processor)

    def test_get_vertices_ids(self):
        leaf_ids = [self.default_tree_vertex_processor.get_vertex_id(vertex=node) for node in self.leaf_nodes_binary_tree_sorted]
        non_leaf_ids = [self.default_tree_vertex_processor.get_vertex_id(vertex=node) for node in self.non_leaf_nodes_binary_tree]
        self.assertEqual(len(leaf_ids), 5)
        self.assertEqual(len(set(leaf_ids)), 5)
        self.assertEqual(len(non_leaf_ids), 4)
        self.assertEqual((len(set(non_leaf_ids))), 4)
        for leaf_id in leaf_ids:
            self.assertNotIn(leaf_id, non_leaf_ids)
        for non_leaf_id in non_leaf_ids:
            self.assertNotIn(non_leaf_id, leaf_ids)

    def test_leaf_node_graphviz_entry_plain(self):
        v = self.leaf_nodes_binary_tree_sorted[0]
        str_color = self.default_tree_vertex_shape_processor.get_color_as_string(entry=v)
        v_id = self.default_tree_vertex_processor.get_vertex_id(vertex=v)
        expected = "\"" + str(v_id) + "\" [label=\"a\", fontname=\"Arial\", " \
                                      "fontsize=\"12\", fontcolor=\"" + str_color + "\", " \
                                                                                    "shape=\"oval\", penwidth=\"3\", style=\"solid\", color=\"" + str_color + "\"];"
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v), expected)
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v, label_format=LabelFormat.plain), expected)
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v, label_format="plain"), expected)

    def test_leaf_node_graphviz_entry_html(self):
        v = self.leaf_nodes_binary_tree_sorted[0]
        str_color = self.default_tree_vertex_shape_processor.get_color_as_string(entry=v)
        v_id = self.default_tree_vertex_processor.get_vertex_id(vertex=v)
        expected = "\"" + str(v_id) + "\" [label=<a>, fontname=\"Arial\", " \
                                      "fontsize=\"12\", fontcolor=\"" + str_color + "\", " \
                                                                                    "shape=\"oval\", penwidth=\"3\", style=\"solid\", color=\"" + str_color + "\"];"
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v, label_format=LabelFormat.html), expected)
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v, label_format="html"), expected)

    def test_non_leaf_graphviz_entry_plain(self):
        v = self.non_leaf_nodes_binary_tree[0]
        str_color = self.default_tree_vertex_shape_processor.get_color_as_string(entry=v)
        v_id = self.default_tree_vertex_processor.get_vertex_id(vertex=v)
        expected = "\"" + str(v_id) + "\" [label=\"\", fontname=\"Arial\", " \
                                      "fontsize=\"12\", fontcolor=\"" + str_color + "\", " \
                                                                                    "shape=\"oval\", penwidth=\"1\", style=\"solid\", color=\"" + str_color + "\"];"
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v), expected)
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v, label_format=LabelFormat.plain), expected)
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v, label_format="plain"), expected)

    def test_non_leaf_graphviz_entry_html(self):
        v = self.non_leaf_nodes_binary_tree[0]
        str_color = self.default_tree_vertex_shape_processor.get_color_as_string(entry=v)
        v_id = self.default_tree_vertex_processor.get_vertex_id(vertex=v)
        expected = "\"" + str(v_id) + "\" [label=<>, fontname=\"Arial\", " \
                                      "fontsize=\"12\", fontcolor=\"" + str_color + "\", " \
                                                                                    "shape=\"oval\", penwidth=\"1\", style=\"solid\", color=\"" + str_color + "\"];"
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v, label_format=LabelFormat.html), expected)
        self.assertEqual(self.default_tree_vertex_processor.export_vertex_as_dot(vertex=v, label_format="html"), expected)


class BGTreeEdgeShapeProcessorTestCase(BGTreeTestCase):
    def setUp(self):
        super(BGTreeEdgeShapeProcessorTestCase, self).setUp()
        self.default_tree_edge_shape_processor = BGTreeEdgeShapeProcessor()

    def test_color_attrib_template(self):
        self.assertEqual("color=\"{color}\"", self.default_tree_edge_shape_processor.color_attrib_template)

    def test_style_attrib_template(self):
        self.assertEqual("style=\"{style}\"", self.default_tree_edge_shape_processor.style_attrib_template)

    def test_pen_width_attrib_template(self):
        self.assertEqual("penwidth=\"{pen_width}\"", self.default_tree_edge_shape_processor.pen_width_attrib_template)

    def test_get_color_non_leaf_branch(self):
        non_leaf_branches_colors = [self.default_tree_edge_shape_processor.get_color_as_string(entry=edge) for edge in
                                    self.non_leaf_branches_binary_tree]
        self.assertEqual(len(non_leaf_branches_colors), 3)
        self.assertEqual(len(set(non_leaf_branches_colors)), 1)

    def test_get_color_leaf_branch_no_color_source(self):
        leaf_branches_colors = [self.default_tree_edge_shape_processor.get_color_as_string(entry=edge) for edge in
                                self.non_leaf_branches_binary_tree]
        self.assertEqual(len(leaf_branches_colors), 3)
        self.assertEqual(len(set(leaf_branches_colors)), 1)

    def test_get_color_leaf_branch_with_color_source(self):
        vsp = BGVertexShapeProcessor()
        genome_colors = []
        for cnt, genome in enumerate([BGGenome("x"), BGGenome("y"), BGGenome("z")] + self.sorted_genomes):
            if cnt > 2:
                genome_colors.append(vsp.get_color_as_string(entry=genome))
        tree_shape_processor = BGTreeEdgeShapeProcessor(color_source=vsp.color_source)
        leaf_branch_colors = [tree_shape_processor.get_color_as_string(entry=edge) for edge in self.leaf_branches_binary_tree]
        self.assertEqual(len(leaf_branch_colors), 5)
        self.assertEqual(len(set(leaf_branch_colors)), 5)
        for genome_color in genome_colors:
            self.assertIn(genome_color, leaf_branch_colors)
        for leaf_branch_color in leaf_branch_colors:
            self.assertIn(leaf_branch_color, genome_colors)

    def test_get_color_for_all_branches_in_tree_no_source(self):
        non_leaf_branches_colors = [self.default_tree_edge_shape_processor.get_color_as_string(entry=edge) for edge in
                                    self.non_leaf_branches_binary_tree]
        leaf_branches_colors = [self.default_tree_edge_shape_processor.get_color_as_string(entry=edge) for edge in
                                self.leaf_branches_binary_tree]
        self.assertEqual(len(leaf_branches_colors), 5)
        self.assertEqual(len(set(leaf_branches_colors)), 5)
        self.assertEqual(len(non_leaf_branches_colors), 3)
        self.assertEqual(len(set(non_leaf_branches_colors)), 1)
        for non_leaf_branch_color in non_leaf_branches_colors:
            self.assertNotIn(non_leaf_branch_color, leaf_branches_colors)
        for leaf_branches_color in leaf_branches_colors:
            self.assertNotIn(leaf_branches_color, non_leaf_branches_colors)

    def test_get_color_for_all_branches_in_tree_with_color_source(self):
        pass

    def test_get_pen_width_non_leaf_branch(self):
        self.assertEqual(1, self.default_tree_edge_shape_processor.get_pen_width(entry=self.non_leaf_branches_binary_tree[0]))

    def test_get_pen_width_leaf_branch(self):
        self.assertEqual(3, self.default_tree_edge_shape_processor.get_pen_width(entry=self.leaf_branches_binary_tree[0]))

    def test_get_style_non_leaf_branch(self):
        self.assertEqual("solid", self.default_tree_edge_shape_processor.get_style(entry=self.non_leaf_branches_binary_tree[0]))

    def test_get_style_leaf_branch(self):
        self.assertEqual("solid", self.default_tree_edge_shape_processor.get_style(entry=self.leaf_branches_binary_tree[0]))

    def test_get_attributes_string_list_non_leaf_branch(self):
        color_str = self.default_tree_edge_shape_processor.get_color_as_string(entry=self.non_leaf_branches_binary_tree[0])
        self.assertSetEqual({"color=\"" + color_str + "\"", "style=\"solid\"", "penwidth=\"1\""},
                            set(self.default_tree_edge_shape_processor.get_attributes_string_list(
                                entry=self.non_leaf_branches_binary_tree[0])))

    def test_get_attribute_string_list_leaf_branch(self):
        color_str = self.default_tree_edge_shape_processor.get_color_as_string(entry=self.leaf_branches_binary_tree[0])
        self.assertSetEqual({"color=\"" + color_str + "\"", "style=\"solid\"", "penwidth=\"3\""},
                            set(self.default_tree_edge_shape_processor.get_attributes_string_list(entry=self.leaf_branches_binary_tree[0])))


class BGTreeEdgeTextProcessorTestCase(BGTreeTestCase):
    def setUp(self):
        super(BGTreeEdgeTextProcessorTestCase, self).setUp()
        self.default_tree_edge_text_processor = BGTreeEdgeTextProcessor()

    def test_font_name_attrib_template(self):
        self.assertEqual("fontname=\"{font}\"", self.default_tree_edge_text_processor.font_attrib_template)

    def test_font_size_attrib_tempalte(self):
        self.assertEqual("fontsize=\"{size}\"", self.default_tree_edge_text_processor.size_attrib_template)

    def test_font_color_attrib_template(self):
        self.assertEqual("fontcolor=\"{color}\"", self.default_tree_edge_text_processor.color_attrib_template)

    def test_get_text_non_leaf_branch_plain(self):
        self.assertEqual("\"\"", self.default_tree_edge_text_processor.get_text(entry=self.non_leaf_branches_binary_tree[0]))
        self.assertEqual("\"\"", self.default_tree_edge_text_processor.get_text(entry=self.non_leaf_branches_binary_tree[0],
                                                                                label_format=LabelFormat.plain))
        self.assertEqual("\"\"",
                         self.default_tree_edge_text_processor.get_text(entry=self.non_leaf_branches_binary_tree[0], label_format="plain"))

    def test_get_text_non_leaf_branch_html(self):
        self.assertEqual("<>", self.default_tree_edge_text_processor.get_text(entry=self.non_leaf_branches_binary_tree[0],
                                                                              label_format=LabelFormat.html))
        self.assertEqual("<>", self.default_tree_edge_text_processor.get_text(entry=self.non_leaf_branches_binary_tree[0],
                                                                              label_format="html"))

    def test_get_text_leaf_branch_plain(self):
        self.assertEqual("\"\"", self.default_tree_edge_text_processor.get_text(entry=self.leaf_branches_binary_tree[0]))
        self.assertEqual("\"\"", self.default_tree_edge_text_processor.get_text(entry=self.leaf_branches_binary_tree[0],
                                                                                label_format=LabelFormat.plain))
        self.assertEqual("\"\"", self.default_tree_edge_text_processor.get_text(entry=self.leaf_branches_binary_tree[0],
                                                                                label_format="plain"))

    def test_get_text_leaf_branch_html(self):
        self.assertEqual("<>", self.default_tree_edge_text_processor.get_text(entry=self.leaf_branches_binary_tree[0],
                                                                              label_format=LabelFormat.html))
        self.assertEqual("<>", self.default_tree_edge_text_processor.get_text(entry=self.leaf_branches_binary_tree[0],
                                                                              label_format="html"))

    def test_get_font_color_non_leaf_branches(self):
        non_leaf_branches_colors = [self.default_tree_edge_text_processor.get_text_color(entry=edge) for edge in
                                    self.non_leaf_branches_binary_tree]
        self.assertEqual(len(non_leaf_branches_colors), 3)
        self.assertEqual(len(set(non_leaf_branches_colors)), 1)

    def test_get_font_color_leaf_branches(self):
        leaf_branches_colors = [self.default_tree_edge_text_processor.get_text_color(entry=edge) for edge in
                                self.leaf_branches_binary_tree]
        self.assertEqual(len(leaf_branches_colors), 5)
        self.assertEqual(len(set(leaf_branches_colors)), 1)

    def test_get_font_size_non_leaf_branches(self):
        self.assertEqual(7, self.default_tree_edge_text_processor.get_text_size(entry=self.non_leaf_branches_binary_tree[0]))

    def test_get_font_size_leaf_branches(self):
        self.assertEqual(7, self.default_tree_edge_text_processor.get_text_size(entry=self.leaf_branches_binary_tree[0]))

    def test_get_font_name_non_leaf_branches(self):
        self.assertEqual("Arial", self.default_tree_edge_text_processor.get_text_font(entry=self.non_leaf_branches_binary_tree[0]))

    def test_get_font_name_leaf_branches(self):
        self.assertEqual("Arial", self.default_tree_edge_text_processor.get_text_font(entry=self.leaf_branches_binary_tree[0]))

    def test_get_attribute_string_list_non_leaf_plain(self):
        self.assertSetEqual({"label=\"\"", "fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\""},
                            set(self.default_tree_edge_text_processor.get_attributes_string_list(
                                entry=self.non_leaf_branches_binary_tree[0])))

    def test_get_attribute_string_list_non_leaf_html(self):
        self.assertSetEqual({"label=<>", "fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\""},
                            set(self.default_tree_edge_text_processor.get_attributes_string_list(
                                entry=self.non_leaf_branches_binary_tree[0],
                                label_format=LabelFormat.html)))

    def test_get_attribute_string_list_leaf_plain(self):
        self.assertSetEqual({"label=\"\"", "fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\""},
                            set(self.default_tree_edge_text_processor.get_attributes_string_list(entry=self.leaf_branches_binary_tree[0])))

    def test_get_attribute_string_list_leaf_html(self):
        self.assertSetEqual({"label=<>", "fontname=\"Arial\"", "fontsize=\"7\"", "fontcolor=\"black\""},
                            set(self.default_tree_edge_text_processor.get_attributes_string_list(entry=self.leaf_branches_binary_tree[0],
                                                                                                 label_format=LabelFormat.html)))


class BGTreeEdgeProcessorTestCase(BGTreeTestCase):
    def setUp(self):
        super(BGTreeEdgeProcessorTestCase, self).setUp()
        self.default_tree_edge_shape_processor = BGTreeEdgeShapeProcessor()
        self.default_tree_edge_text_processor = BGTreeEdgeTextProcessor()
        self.default_vertex_processor = BGTreeVertexProcessor()
        self.default_tree_edge_processor = BGTreeEdgeProcessor(vertex_processor=self.default_vertex_processor)

    def test_edge_shape_processor_field(self):
        self.assertIsInstance(self.default_tree_edge_processor.shape_processor, ShapeProcessor)

    def test_edge_text_processor_field(self):
        self.assertIsInstance(self.default_tree_edge_processor.text_processor, TextProcessor)

    def test_overall_template(self):
        self.assertEqual("\"{v1_id}\" -- \"{v2_id}\" [{attributes}];", self.default_tree_edge_processor.template)

    def test_non_leaf_branch_graphviz_entry_no_color_source_plain(self):
        colors = []
        for branch in self.non_leaf_branches_binary_tree:
            color_str = self.default_tree_edge_processor.shape_processor.color_source.get_color_as_string(entry=None)
            colors.append(color_str)
            v1, v2 = branch
            v1_id, v2_id = self.default_tree_edge_processor.vertex_processor.get_vertex_id(
                vertex=v1), self.default_tree_edge_processor.vertex_processor.get_vertex_id(vertex=v2)
            expected = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + color_str + "\", style=\"solid\", penwidth=\"1\"];"
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch)[0], expected)
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch, label_format="plain")[0], expected)
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch, label_format=LabelFormat.plain)[0], expected)
        self.assertEqual(len(colors), 3)
        self.assertEqual(len(set(colors)), 1)

    def test_leaf_branch_graphviz_entry_no_color_course_plain(self):
        colors = []
        for branch in self.leaf_branches_binary_tree:
            entry = branch[0] if not isinstance(branch[0], TreeNode) else branch[1]
            color_str = self.default_tree_edge_processor.shape_processor.color_source.get_color_as_string(entry=entry)
            colors.append(color_str)
            v1, v2 = branch
            v1_id, v2_id = self.default_tree_edge_processor.vertex_processor.get_vertex_id(
                vertex=v1), self.default_tree_edge_processor.vertex_processor.get_vertex_id(vertex=v2)
            expected = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + color_str + "\", style=\"solid\", penwidth=\"3\"];"
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch)[0], expected)
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch, label_format="plain")[0], expected)
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch, label_format=LabelFormat.plain)[0], expected)
        self.assertEqual(len(colors), 5)
        self.assertEqual(len(set(colors)), 5)

    def test_non_leaf_branch_graphviz_entry_no_color_source_html(self):
        colors = []
        for branch in self.non_leaf_branches_binary_tree:
            color_str = self.default_tree_edge_processor.shape_processor.color_source.get_color_as_string(entry=None)
            colors.append(color_str)
            v1, v2 = branch
            v1_id, v2_id = self.default_tree_edge_processor.vertex_processor.get_vertex_id(
                vertex=v1), self.default_tree_edge_processor.vertex_processor.get_vertex_id(vertex=v2)
            expected = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + color_str + "\", style=\"solid\", penwidth=\"1\"];"
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch, label_format="html")[0], expected)
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch, label_format=LabelFormat.html)[0], expected)
        self.assertEqual(len(colors), 3)
        self.assertEqual(len(set(colors)), 1)

    def test_leaf_branch_graphviz_entry_no_color_course_html(self):
        colors = []
        for branch in self.leaf_branches_binary_tree:
            entry = branch[0] if not isinstance(branch[0], TreeNode) else branch[1]
            color_str = self.default_tree_edge_processor.shape_processor.color_source.get_color_as_string(entry=entry)
            colors.append(color_str)
            v1, v2 = branch
            v1_id, v2_id = self.default_tree_edge_processor.vertex_processor.get_vertex_id(
                vertex=v1), self.default_tree_edge_processor.vertex_processor.get_vertex_id(vertex=v2)
            expected = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + color_str + "\", style=\"solid\", penwidth=\"3\"];"
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch, label_format="html")[0], expected)
            self.assertEqual(self.default_tree_edge_processor.export_edge_as_dot(edge=branch, label_format=LabelFormat.html)[0], expected)
        self.assertEqual(len(colors), 5)
        self.assertEqual(len(set(colors)), 5)

    def populate_color_source(self):
        color_source = ColorSource()
        non_leaf_genome_colors = [color_source.get_color_as_string(entry=genome) for genome in
                                  [BGGenome("x"), BGGenome("y"), BGGenome("z")]]
        genome_colors = [color_source.get_color_as_string(entry=genome) for genome in self.sorted_genomes]
        return color_source, non_leaf_genome_colors, genome_colors

    def test_non_leaf_branch_graphviz_entry_with_color_source_plain(self):
        color_source, non_leaf_genome_colors, genome_colors = self.populate_color_source()
        colors = []
        tree_edge_processor = BGTreeEdgeProcessor(vertex_processor=self.default_vertex_processor, color_source=color_source)
        for branch in self.non_leaf_branches_binary_tree:
            color_str = tree_edge_processor.shape_processor.color_source.get_color_as_string(entry=None)
            colors.append(color_str)
            v1, v2 = branch
            v1_id, v2_id = tree_edge_processor.vertex_processor.get_vertex_id(
                vertex=v1), tree_edge_processor.vertex_processor.get_vertex_id(vertex=v2)
            expected = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + color_str + "\", style=\"solid\", penwidth=\"1\"];"
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch)[0], expected)
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch, label_format="plain")[0], expected)
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch, label_format=LabelFormat.plain)[0], expected)
        self.assertEqual(len(colors), 3)
        self.assertEqual(len(set(colors)), 1)
        for entry in colors:
            self.assertNotIn(entry, non_leaf_genome_colors)
            self.assertNotIn(entry, genome_colors)

    def test_non_leaf_branch_graphviz_entry_with_color_source_html(self):
        color_source, non_leaf_genome_colors, genome_colors = self.populate_color_source()
        colors = []
        tree_edge_processor = BGTreeEdgeProcessor(vertex_processor=self.default_vertex_processor, color_source=color_source)
        for branch in self.non_leaf_branches_binary_tree:
            color_str = tree_edge_processor.shape_processor.color_source.get_color_as_string(entry=None)
            colors.append(color_str)
            v1, v2 = branch
            v1_id, v2_id = tree_edge_processor.vertex_processor.get_vertex_id(
                vertex=v1), tree_edge_processor.vertex_processor.get_vertex_id(vertex=v2)
            expected = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + color_str + "\", style=\"solid\", penwidth=\"1\"];"
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch, label_format="html")[0], expected)
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch, label_format=LabelFormat.html)[0], expected)
        self.assertEqual(len(colors), 3)
        self.assertEqual(len(set(colors)), 1)
        for entry in colors:
            self.assertNotIn(entry, non_leaf_genome_colors)
            self.assertNotIn(entry, genome_colors)

    def test_leaf_branch_graphviz_entry_with_color_source_plain(self):
        color_source, non_leaf_genome_colors, genome_colors = self.populate_color_source()
        colors = []
        tree_edge_processor = BGTreeEdgeProcessor(vertex_processor=self.default_vertex_processor, color_source=color_source)
        for branch in self.leaf_branches_binary_tree:
            entry = branch[0] if not isinstance(branch[0], TreeNode) else branch[1]
            color_str = tree_edge_processor.shape_processor.color_source.get_color_as_string(entry=entry)
            colors.append(color_str)
            v1, v2 = branch
            v1_id, v2_id = tree_edge_processor.vertex_processor.get_vertex_id(
                vertex=v1), tree_edge_processor.vertex_processor.get_vertex_id(vertex=v2)
            expected = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + color_str + "\", style=\"solid\", penwidth=\"3\"];"
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch)[0], expected)
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch, label_format="plain")[0], expected)
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch, label_format=LabelFormat.plain)[0], expected)
        self.assertEqual(len(colors), 5)
        self.assertEqual(len(set(colors)), 5)
        self.assertSetEqual(set(genome_colors), set(colors))
        for entry in colors:
            self.assertNotIn(entry, non_leaf_genome_colors)
            self.assertIn(entry, genome_colors)

    def test_leaf_branch_graphviz_entry_with_color_source_html(self):
        color_source, non_leaf_genome_colors, genome_colors = self.populate_color_source()
        colors = []
        tree_edge_processor = BGTreeEdgeProcessor(vertex_processor=self.default_vertex_processor, color_source=color_source)
        for branch in self.leaf_branches_binary_tree:
            entry = branch[0] if not isinstance(branch[0], TreeNode) else branch[1]
            color_str = tree_edge_processor.shape_processor.color_source.get_color_as_string(entry=entry)
            colors.append(color_str)
            v1, v2 = branch
            v1_id, v2_id = tree_edge_processor.vertex_processor.get_vertex_id(
                vertex=v1), tree_edge_processor.vertex_processor.get_vertex_id(vertex=v2)
            expected = "\"" + str(v1_id) + "\" -- \"" + str(v2_id) + "\" [color=\"" + color_str + "\", style=\"solid\", penwidth=\"3\"];"
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch, label_format="html")[0], expected)
            self.assertEqual(tree_edge_processor.export_edge_as_dot(edge=branch, label_format=LabelFormat.html)[0], expected)
        self.assertEqual(len(colors), 5)
        self.assertEqual(len(set(colors)), 5)
        self.assertSetEqual(set(genome_colors), set(colors))
        for entry in colors:
            self.assertNotIn(entry, non_leaf_genome_colors)
            self.assertIn(entry, genome_colors)


class BGTreeProcessorTestCase(BGTreeTestCase):
    def setUp(self):
        super(BGTreeProcessorTestCase, self).setUp()
        self.default_tree_vertex_processor = BGTreeVertexProcessor()
        self.default_tree_edge_processor = BGTreeEdgeProcessor(vertex_processor=self.default_tree_vertex_processor)
        self.default_tree_processor = BGTreeProcessor(vertex_processor=self.default_tree_vertex_processor,
                                                      edge_processor=self.default_tree_edge_processor)

    def test_overall_template(self):
        self.assertEqual("graph {{\n{edges}\n{vertices}\n}}", self.default_tree_processor.template)

    def test_get_vertices_graphviz_entries_plain(self):
        expected = [self.default_tree_vertex_processor.export_vertex_as_dot(vertex=vertex) for vertex in self.leaf_nodes_binary_tree]
        expected.extend(
            [self.default_tree_vertex_processor.export_vertex_as_dot(vertex=vertex) for vertex in self.non_leaf_nodes_binary_tree])
        vertices_graphviz_entries = self.default_tree_processor.export_vertices_as_dot(graph=self.binary_tree)
        self.assertEqual(len(vertices_graphviz_entries), 9)
        for vertex_graphviz_entry in vertices_graphviz_entries:
            self.assertIn(vertex_graphviz_entry, expected)

    def test_get_vertices_graphviz_entries_html(self):
        expected = [self.default_tree_vertex_processor.export_vertex_as_dot(vertex=vertex, label_format=LabelFormat.html) for vertex in
                    self.leaf_nodes_binary_tree]
        expected.extend([self.default_tree_vertex_processor.export_vertex_as_dot(vertex=vertex, label_format=LabelFormat.html) for vertex in
                         self.non_leaf_nodes_binary_tree])
        vertices_graphviz_entries = self.default_tree_processor.export_vertices_as_dot(graph=self.binary_tree,
                                                                                       label_format=LabelFormat.html)
        self.assertEqual(len(vertices_graphviz_entries), 9)
        for vertex_graphviz_entry in vertices_graphviz_entries:
            self.assertIn(vertex_graphviz_entry, expected)

    def test_get_edges_graphviz_entries_plain(self):
        expected = [self.default_tree_edge_processor.export_edge_as_dot(edge=edge)[0] for edge in self.leaf_branches_binary_tree]
        expected.extend([self.default_tree_edge_processor.export_edge_as_dot(edge=edge)[0] for edge in self.non_leaf_branches_binary_tree])
        expected.extend(
            [self.default_tree_edge_processor.export_edge_as_dot(edge=(edge[1], edge[0]))[0] for edge in self.leaf_branches_binary_tree])
        expected.extend(
            [self.default_tree_edge_processor.export_edge_as_dot(edge=(edge[1], edge[0]))[0] for edge in
             self.non_leaf_branches_binary_tree])
        edges_graphviz_entries = self.default_tree_processor.export_edges_as_dot(graph=self.binary_tree)
        self.assertEqual(len(edges_graphviz_entries), 8)
        for edge_graphviz_entry in edges_graphviz_entries:
            self.assertIn(edge_graphviz_entry, expected)

    def test_get_edge_graphviz_entries_html(self):
        expected = [self.default_tree_edge_processor.export_edge_as_dot(edge=edge, label_format=LabelFormat.html)[0] for edge in
                    self.leaf_branches_binary_tree]
        expected.extend(
            [self.default_tree_processor.edge_processor.export_edge_as_dot(edge=edge, label_format=LabelFormat.html)[0] for edge in
             self.non_leaf_branches_binary_tree])
        expected.extend(
            [self.default_tree_edge_processor.export_edge_as_dot(edge=(edge[1], edge[0]), label_format=LabelFormat.html)[0] for edge in
             self.leaf_branches_binary_tree])
        expected.extend(
            [self.default_tree_edge_processor.export_edge_as_dot(edge=(edge[1], edge[0]), label_format=LabelFormat.html)[0] for edge in
             self.non_leaf_branches_binary_tree])
        edges_graphviz_entries = self.default_tree_processor.export_edges_as_dot(graph=self.binary_tree, label_format=LabelFormat.html)
        self.assertEqual(len(edges_graphviz_entries), 8)
        for edge_graphviz_entry in edges_graphviz_entries:
            self.assertIn(edge_graphviz_entry, expected)


if __name__ == '__main__':
    unittest.main()
