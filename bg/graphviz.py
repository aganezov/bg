# -*- coding: utf-8 -*-
from collections import deque
from enum import Enum

from ete3 import TreeNode

from bg import Multicolor
from bg.breakpoint_graph import BreakpointGraph
from bg.edge import BGEdge
from bg.genome import BGGenome
from bg.vertices import BGVertex, InfinityVertex, TaggedInfinityVertex


def vertex_as_a_sting(vertex):
    result = ""
    if isinstance(vertex, BGVertex):
        orientation = "t" if vertex.is_tail_vertex else "h"
        result += vertex.block_name + orientation
        if vertex.is_tagged_vertex and len(vertex.tags) > 0:
            result += " " + " ".join(map(lambda entry: "(" + entry + ")", vertex.get_tags_as_list_of_strings()))
    else:
        result = str(vertex)
    return "{string}".format(string=result)


def vertex_as_html(vertex):
    result = ""
    if isinstance(vertex, BGVertex):
        if vertex.is_block_vertex:
            orientation = "t" if vertex.is_tail_vertex else "h"
            result += vertex.block_name + "<SUP>" + orientation + "</SUP>"
        if vertex.is_tagged_vertex and len(vertex.tags) > 0:
            result += " " + " ".join(map(lambda entry: "(" + entry + ")", vertex.get_tags_as_list_of_strings()))
    else:
        result = str(vertex)
    return "<" + result + ">"


class LabelFormat(Enum):
    plain = "plain"
    html = "html"


class Colors(Enum):
    black = "black"  # 0
    red = "red"  # 1
    green = "lawngreen"  # 2
    teal = "teal"  # 3
    navy = "navy"  # 4
    aqua = "aqua"  # 5
    magenta = "magenta"  # 6
    chocolate = "chocolate"  # 7
    wheat = "wheat"  # 8
    violet = "violet"  # 9
    orange = "orange"  # 10
    lightpink = "lightpink"  # 11
    aliceblue = "aliceblue"  # 12
    antiquewhite = "antiquewhite"  # 13
    aquamarine = "aquamarine"  # 14
    brown = "brown"  # 15
    darkcyan = "darkcyan"  # 16
    deepskyblue = "deepskyblue"  # 17
    gold = "gold"  # 18
    lightcoral = "lightcoral"  # 19
    mediumpurple = "mediumpurple"  # 20
    mediumslateblue = "mediumslateblue"  # 21
    mediumturquoise = "mediumturquoise"  # 22
    navajowhite = "navajowhite"  # 23
    palegoldenrod = "palegoldenrod"  # 24
    silver = "silver"  # 25
    yellowgreen = "yellowgreen"  # 26
    rosybrown = "rosybrown"  # 27
    slateblue = "slateblue"  # 28
    forestgreen = "forestgreen"  # 29
    snow = "snow"  # 30


def ids_generator(start=1, step=1):
    while True:
        yield start
        start += step


class ColorSource(object):
    def __init__(self):
        self.color_to_dot_color = {}
        self.unused_colors = deque([
            Colors.black,
            Colors.red,
            Colors.green,
            Colors.teal,
            Colors.navy,
            Colors.aqua,
            Colors.magenta,
            Colors.chocolate,
            Colors.wheat,
            Colors.violet,
            Colors.orange,
            Colors.lightpink,
            Colors.aliceblue,
            Colors.antiquewhite,
            Colors.aquamarine,
            Colors.brown,
            Colors.darkcyan,
            Colors.deepskyblue,
            Colors.gold,
            Colors.lightcoral,
            Colors.mediumpurple,
            Colors.mediumslateblue,
            Colors.mediumturquoise,
            Colors.navajowhite,
            Colors.palegoldenrod,
            Colors.silver,
            Colors.yellowgreen,
            Colors.rosybrown,
            Colors.slateblue,
            Colors.forestgreen,
            Colors.snow
        ])

    def get_unused_color(self, entry):
        if entry not in self.color_to_dot_color:
            self.color_to_dot_color[entry] = self.unused_colors.popleft()
        return self.color_to_dot_color[entry]

    def get_color_as_string(self, entry):
        return self.get_unused_color(entry=entry).value


class ShapeProcessor:
    def __init__(self, pen_width=1, style="solid", color=Colors.black, color_source=None):
        self.style_attrib_template = "style=\"{style}\""
        self.color_attrib_template = "color=\"{color}\""
        self.color_source = color_source if color_source is not None else ColorSource()
        self.pen_width = pen_width
        self.style = style
        self.color = color
        self.pen_width_attrib_template = "penwidth=\"{pen_width}\""

    def get_pen_width(self, entry=None):
        return self.pen_width

    def get_style(self, entry=None):
        return "solid"

    def get_color_as_string(self, entry):
        return self.color_source.get_color_as_string(entry=entry)


class TextProcessor:
    def __init__(self, color=Colors.black, size=12, font_name="Arial"):
        self.color = color
        self.text_size = size
        self.text_font_name = font_name

        self.color_attrib_template = "fontcolor=\"{color}\""
        self.size_attrib_template = "fontsize=\"{size}\""
        self.font_attrib_template = "fontname=\"{font}\""
        self.label_attrib_template = "label={label}"

    def get_text_font(self, entry=None):
        return self.text_font_name

    def get_text_size(self, entry=None):
        return self.text_size

    def get_text_color(self, entry=None):
        return self.color.value if self.color in Colors else str(self.color)

    def get_text(self, entry=None, label_format=LabelFormat.plain):
        if label_format == LabelFormat.html.value or label_format == LabelFormat.html:
            return "<>"
        return "\"\""

    def get_attributes_string_list(self, entry, label_format=LabelFormat.plain):
        return [self.label_attrib_template.format(label=self.get_text(entry=entry, label_format=label_format)),
                self.font_attrib_template.format(font=self.text_font_name),
                self.size_attrib_template.format(size=self.text_size),
                self.color_attrib_template.format(color=self.get_text_color(entry=entry))]


class VertexShapeProcessor(ShapeProcessor):
    def __init__(self, pen_width=1, style="solid", color=Colors.black, shape="oval", color_source=None):
        super().__init__(pen_width=pen_width, style=style, color=color, color_source=color_source)
        self.shape_attrib_template = "shape=\"{shape}\""
        self.shape = shape

    def get_shape(self, entry=None):
        return self.shape

    def get_attributes_string_list(self, entry):
        return [self.shape_attrib_template.format(shape=self.get_shape(entry=entry)),
                self.pen_width_attrib_template.format(pen_width=self.get_pen_width(entry=entry)),
                self.style_attrib_template.format(style=self.get_style(entry=entry)),
                self.color_attrib_template.format(color=self.get_color_as_string(entry=entry))]


class BGVertexShapeProcessor(VertexShapeProcessor):
    def __init__(self, pen_width=1, style="solid", color=Colors.black, color_source=None,
                 regular_vertex_shape="oval", irregular_vertex_shape="point", non_bg_vertex_shape="oval"):
        super().__init__(pen_width=pen_width, style=style, color=color, shape=non_bg_vertex_shape, color_source=color_source)
        self.regular_vertex_shape = regular_vertex_shape
        self.irregular_vertex_shape = irregular_vertex_shape

    def get_shape(self, entry=None):
        if isinstance(entry, BGVertex):
            return self.regular_vertex_shape if entry.is_regular_vertex else self.irregular_vertex_shape
        return super().get_shape(entry=entry)

    def get_attributes_string_list(self, entry):
        return [self.shape_attrib_template.format(shape=self.get_shape(entry=entry)),
                self.pen_width_attrib_template.format(pen_width=self.get_pen_width())]


class BGVertexTextProcessor(TextProcessor):
    def __init__(self, color=Colors.black, size=12, font_name="Arial"):
        super().__init__(color=color, size=size, font_name=font_name)

    def get_text(self, entry=None, label_format=LabelFormat.plain):
        if entry is None:
            return super().get_text(entry=entry, label_format=label_format)
        if label_format == LabelFormat.plain.value or label_format == LabelFormat.plain:
            return "\"" + vertex_as_a_sting(vertex=entry) + "\""
        elif label_format == LabelFormat.html.value or label_format == LabelFormat.html:
            return vertex_as_html(vertex=entry)


class VertexProcessor(object):
    def __init__(self, shape_processor=None, text_processor=None):
        self.vertices_id_generator = ids_generator()
        self.vertices_ids_storage = {}
        self.shape_processor = shape_processor
        self.text_processor = text_processor
        self.template = "\"{v_id}\" [{attributes}];"

    def get_vertex_id(self, vertex):
        if vertex not in self.vertices_ids_storage:
            self.vertices_ids_storage[vertex] = next(self.vertices_id_generator)
        return self.vertices_ids_storage[vertex]

    def export_vertex_as_dot(self, vertex, label_format=LabelFormat.plain):
        """

        :type label_format: Union[str, LabelFormat]
        """
        vertex_id = self.get_vertex_id(vertex=vertex)
        attributes = []
        attributes.extend(self.text_processor.get_attributes_string_list(entry=vertex, label_format=label_format))
        attributes.extend(self.shape_processor.get_attributes_string_list(entry=vertex))
        return self.template.format(v_id=vertex_id, attributes=", ".join(attributes))


class BGVertexProcessor(VertexProcessor):
    def __init__(self, shape_processor=None, text_processor=None):
        super().__init__(shape_processor=shape_processor, text_processor=text_processor)
        self.shape_processor = shape_processor if shape_processor is not None else BGVertexShapeProcessor()
        self.text_processor = text_processor if text_processor is not None else BGVertexTextProcessor()

    def get_vertex_id(self, vertex):
        if isinstance(vertex, InfinityVertex):
            vertex = BGVertex.get_vertex_name_root(vertex.name)
        return super().get_vertex_id(vertex=vertex)

    def export_vertex_as_dot(self, vertex, label_format=LabelFormat.plain):
        """

        :type label_format: Union[str, LabelFormat]
        """
        vertex_id = self.get_vertex_id(vertex=vertex)
        attributes = []
        if not isinstance(vertex, InfinityVertex):
            attributes.extend(self.text_processor.get_attributes_string_list(entry=vertex, label_format=label_format))
        attributes.extend(self.shape_processor.get_attributes_string_list(entry=vertex))
        return self.template.format(v_id=vertex_id, attributes=", ".join(attributes))


class EdgeShapeProcessor(ShapeProcessor):
    def __init__(self):
        super().__init__()
        self.regular_edge_style = "solid"
        self.irregular_edge_style = "dotted"
        self.repeat_edge_style = "dashed"
        self.regular_edge_pen_width = 1
        self.irregular_edge_pen_with = .1
        self.repeat_edge_pen_width = .5

    def get_style(self, entry=None):
        if entry is None or not isinstance(entry, BGEdge):
            return self.regular_edge_style
        if entry.is_repeat_edge:
            return self.repeat_edge_style
        if entry.is_irregular_edge:
            return self.irregular_edge_style
        if entry.is_regular_edge:
            return self.regular_edge_style

    def get_pen_width(self, entry=None):
        if entry is None or not isinstance(entry, BGEdge):
            return self.regular_edge_pen_width
        if entry.is_repeat_edge:
            return self.repeat_edge_pen_width
        if entry.is_irregular_edge:
            return self.irregular_edge_pen_with
        if entry.is_regular_edge:
            return self.regular_edge_pen_width

    def get_dot_colors(self, multicolor):
        return [self.color_source.get_unused_color(entry=color) for color in multicolor.multicolors.elements()]

    def get_attributes_string_list(self, entry):
        if len(list(entry.multicolor.multicolors.elements())) != 1:
            raise ValueError(
                "Graphviz edge shape attributes can not be created only for multi-colored edge, but rather an edge with a single-colored edge")
        color = self.get_dot_colors(multicolor=entry.multicolor)[0].value
        return [
            self.color_attrib_template.format(color=color),
            self.style_attrib_template.format(style=self.get_style(entry=entry)),
            self.pen_width_attrib_template.format(pen_width=self.get_pen_width(entry=entry))]


class EdgeTextProcessor(TextProcessor):
    def __init__(self, size=7, font_name="Arial", color=Colors.black):
        super().__init__(size=size, font_name=font_name, color=color)

    def get_text(self, entry=None, label_format=LabelFormat.plain, tag_key_processor=None, tag_value_processor=None):
        """

        :type label_format: Union[str, LabelFormat]
        """
        if entry is None or not isinstance(entry, BGEdge):
            return super().get_text(entry=entry, label_format=label_format)
        if tag_key_processor is None:
            tag_key_processor = self._tag_key_processor
        if tag_value_processor is None:
            tag_value_processor = self._tag_value_processor
        text = ""
        if isinstance(entry.vertex1, TaggedInfinityVertex):
            for tag, value in entry.vertex1.tags:
                text += tag_key_processor(tag, label_format=label_format) + \
                        entry.vertex1.TAG_SEPARATOR + \
                        tag_value_processor(value, label_format=label_format)
        if isinstance(entry.vertex2, TaggedInfinityVertex):
            for tag, value in entry.vertex2.tags:
                text += " " if len(text) > 0 else ""
                text += tag_key_processor(tag, label_format=label_format) + \
                        entry.vertex1.TAG_SEPARATOR + \
                        tag_value_processor(value, label_format=label_format)
        if label_format == LabelFormat.plain.value or label_format == LabelFormat.plain:
            return "\"" + text + "\""
        elif label_format == LabelFormat.html.value or label_format == LabelFormat.html:
            return "<" + text + ">"
        return "\"\""

    def _tag_key_processor(self, key, label_format):
        if key == "repeat":
            return "r"
        else:
            return str(key)

    def _tag_value_processor(self, value, label_format):
        if str(value).endswith(("h", "t")) and (label_format == LabelFormat.html.value or label_format == LabelFormat.html):
            return str(value)[:-1] + "<SUP>" + str(value)[-1] + "</SUP>"
        return str(value)


class EdgeProcessor(object):
    def __init__(self, vertex_processor, edge_shape_processor=None, edge_text_processor=None):
        self.shape_processor = edge_shape_processor if edge_shape_processor is not None else EdgeShapeProcessor()
        self.text_processor = edge_text_processor if edge_text_processor is not None else EdgeTextProcessor()
        self.vertex_processor = vertex_processor
        self.template = "\"{v1_id}\" -- \"{v2_id}\" [{attributes}];"

    def export_edge_as_dot(self, edge, label_format=LabelFormat.plain):
        """

        :type label_format: Union[str, LabelFormat]
        """
        v1_id = self.vertex_processor.get_vertex_id(vertex=edge.vertex1)
        v2_id = self.vertex_processor.get_vertex_id(vertex=edge.vertex2)
        result = []
        for color in edge.multicolor.multicolors.elements():
            tmp_edge = BGEdge(vertex1=edge.vertex1, vertex2=edge.vertex2, multicolor=Multicolor(color), data=edge.data)
            attributes = self.shape_processor.get_attributes_string_list(entry=tmp_edge)
            if len(self.text_processor.get_text(entry=tmp_edge)) > 2:
                attributes.extend(self.text_processor.get_attributes_string_list(entry=tmp_edge, label_format=label_format))
            result.append(self.template.format(v1_id=v1_id, v2_id=v2_id, attributes=", ".join(attributes)))
        return result


class GraphProcessor(object):
    def __init__(self, vertex_processor=None, edge_processor=None):
        self.vertex_processor = vertex_processor if vertex_processor is not None else BGVertexProcessor()
        self.edge_processor = edge_processor if edge_processor is not None else EdgeProcessor(vertex_processor=self.vertex_processor)
        self.template = "graph {{\n{edges}\n{vertices}\n}}"

    def export_vertices_as_dot(self, graph: BreakpointGraph, label_format="plain"):
        result = []
        for vertex in graph.nodes():
            result.append(self.vertex_processor.export_vertex_as_dot(vertex=vertex, label_format=label_format))
        return result

    def export_edges_as_dot(self, graph: BreakpointGraph, label_format="plain"):
        result = []
        for edge in graph.edges():
            result.extend(self.edge_processor.export_edge_as_dot(edge=edge, label_format=label_format))
        return result

    def export_graph_as_dot(self, graph, label_format="plain"):
        vertices_entries = self.export_vertices_as_dot(graph=graph, label_format=label_format)
        edges_entries = self.export_edges_as_dot(graph=graph, label_format=label_format)
        return self.template.format(edges="\n".join(edges_entries), vertices="\n".join(vertices_entries))


class TreeVertexShapeProcessor(VertexShapeProcessor):
    def __init__(self, color=Colors.black, style="solid", internal_node_pen_width=1, leaf_node_pen_width=3, shape="oval", color_source=None,
                 vertex_data_wrapper=BGGenome):
        super().__init__(color=color, style=style, pen_width=internal_node_pen_width, shape=shape, color_source=color_source)
        self.leaf_node_pen_width = leaf_node_pen_width
        self.internal_node_pen_width = internal_node_pen_width
        self.vertex_data_wrapper = vertex_data_wrapper

    def get_pen_width(self, entry=None):
        if not isinstance(entry, TreeNode):
            return super().get_pen_width(entry=entry)
        if entry.is_leaf():
            return self.leaf_node_pen_width
        else:
            return self.internal_node_pen_width

    def get_color_as_string(self, entry):
        if not isinstance(entry, TreeNode):
            return super().get_color_as_string(entry=entry)
        if entry.is_leaf():
            entry = entry.name
        else:
            entry = None
        return super().get_color_as_string(entry=entry)


class TreeVertexTextProcessor(TextProcessor):
    def __init__(self, color=Colors.black, size=12, font_name="Arial", color_source=None):
        super().__init__(color=color, size=size, font_name=font_name)
        self.color_source = color_source if color_source is not None else ColorSource()

    def get_text_color(self, entry=None):
        if entry is None or not isinstance(entry, TreeNode):
            return super().get_text_color(entry=entry)
        if entry.is_leaf():
            entry = entry.name
        else:
            entry = ""
        return self.color_source.get_color_as_string(entry=entry)

    def get_text(self, entry=None, label_format=LabelFormat.plain):
        if entry is None or not isinstance(entry, TreeNode):
            return super().get_text(entry=entry, label_format=label_format)
        text = ""
        if entry.is_leaf():
            text += entry.name
        if label_format == LabelFormat.html or label_format == LabelFormat.html.value:
            return "<" + text + ">"
        return "\"" + text + "\""


class TreeVertexProcessor(VertexProcessor):
    def __init__(self, shape_processor=None, text_processor=None):
        super().__init__(shape_processor=shape_processor, text_processor=text_processor)
        self.shape_processor = shape_processor if shape_processor is not None else TreeVertexShapeProcessor()
        self.text_processor = text_processor if text_processor is not None else TreeVertexTextProcessor()

    def get_vertex_id(self, vertex):
        return super().get_vertex_id(vertex=vertex)

    def export_vertex_as_dot(self, vertex, label_format=LabelFormat.plain):
        vertex_id = self.get_vertex_id(vertex=vertex)
        attributes = []
        if isinstance(vertex, TreeNode) and vertex.is_leaf():
            attributes.extend(self.text_processor.get_attributes_string_list(entry=vertex, label_format=label_format))
        attributes.extend(self.shape_processor.get_attributes_string_list(entry=vertex))
        return self.template.format(v_id=vertex_id, attributes=", ".join(attributes))


class TreeEdgeShapeProcessor(ShapeProcessor):
    def __init__(self, pen_width=1, color=Colors.black, color_source=None, style="solid"):
        super().__init__(pen_width=pen_width, color=color, color_source=color_source, style=style)