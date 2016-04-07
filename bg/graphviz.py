# -*- coding: utf-8 -*-
from enum import Enum

from bg.edge import BGEdge
from bg.vertices import BGVertex, vertex_as_a_sting, vertex_as_html, InfinityVertex


def ids_generator(start=1, step=1):
    while True:
        yield start
        start += step


class VertexShapeProcessor(object):
    def __init__(self, pen_width=1, regular_vertex_shape="oval", irregular_vertex_shape="point", non_bg_vertex_shape="oval"):
        self.pen_width = pen_width
        self.regular_vertex_shape = regular_vertex_shape
        self.irregular_vertex_shape = irregular_vertex_shape
        self.non_bg_vertex_shape = non_bg_vertex_shape

        self.pen_width_attrib_template = "penwidth=\"{pen_width}\""
        self.shape_attrib_template = "shape=\"{shape}\""

    def get_shape(self, vertex=None):
        if isinstance(vertex, BGVertex):
            return self.regular_vertex_shape if vertex.is_regular_vertex else self.irregular_vertex_shape
        else:
            return self.non_bg_vertex_shape

    def get_pen_width(self):
        return self.pen_width

    def get_attributes_string_list(self, vertex):
        return [self.shape_attrib_template.format(shape=self.get_shape(vertex=vertex)),
                self.pen_width_attrib_template.format(pen_width=self.get_pen_width())]


class VertexTextProcessor(object):
    class VertexTextType(Enum):
        plain = "plain"
        html = "html"

    def __init__(self):
        self.text_color = "black"
        self.text_size = 12
        self.text_font_name = "Arial"

        self.color_attrib_template = "fontcolor=\"{color}\""
        self.size_attrib_template = "fontsize=\"{size}\""
        self.font_attrib_template = "fontname=\"{font}\""
        self.label_attrib_template = "label={label}"

    def get_text_font(self):
        return self.text_font_name

    def get_text_size(self):
        return self.text_size

    def get_text_color(self):
        return self.text_color

    def get_text(self, vertex, label_format=VertexTextType.plain):
        if label_format == self.VertexTextType.plain.value or label_format == self.VertexTextType.plain:
            return "\"" + vertex_as_a_sting(vertex=vertex) + "\""
        elif label_format == self.VertexTextType.html.value or label_format == self.VertexTextType.html:
            return vertex_as_html(vertex=vertex)
        return ""

    def get_attributes_string_list(self, vertex, label_format=VertexTextType.plain):
        return [self.label_attrib_template.format(label=self.get_text(vertex=vertex, label_format=label_format)),
                self.font_attrib_template.format(font=self.text_font_name),
                self.size_attrib_template.format(size=self.text_size),
                self.color_attrib_template.format(color=self.text_color)]


class VertexProcessor(object):
    def __init__(self, shape_processor=None, text_processor=None):
        self.vertices_id_generator = ids_generator()
        self.vertices_ids_storage = {}
        self.shape_processor = shape_processor if shape_processor is not None else VertexShapeProcessor()
        self.text_processor = text_processor if text_processor is not None else VertexTextProcessor()
        self.template = "{v_id} [{attributes}];"

    def get_vertex_id(self, vertex):
        if isinstance(vertex, InfinityVertex):
            vertex = BGVertex.get_vertex_name_root(vertex.name)
        if vertex not in self.vertices_ids_storage:
            self.vertices_ids_storage[vertex] = next(self.vertices_id_generator)
        return self.vertices_ids_storage[vertex]

    def export_vertex_as_dot(self, vertex, label_format=VertexTextProcessor.VertexTextType.plain):
        vertex_id = self.get_vertex_id(vertex=vertex)
        attributes = []
        if not isinstance(vertex, InfinityVertex):
            attributes.extend(self.text_processor.get_attributes_string_list(vertex=vertex, label_format=label_format))
        attributes.extend(self.shape_processor.get_attributes_string_list(vertex=vertex))
        return self.template.format(v_id=vertex_id, attributes=", ".join(attributes))


class EdgeShapeProcessor(object):
    def __init__(self):
        self.regular_edge_style = "solid"
        self.irregular_edge_style = "dotted"
        self.repeat_edge_style = "dashed"
        self.regular_edge_pen_width = 1
        self.irregular_edge_pen_with = .1
        self.repeat_edge_pen_width = .5

        self.style_attribute_template = "style=\"{style}\""
        self.pen_width_attribute_template = "penwidth=\"{pen_width}\""

    def get_style(self, edge=None):
        if edge is None or not isinstance(edge, BGEdge):
            return self.regular_edge_style
        if edge.is_repeat_edge:
            return self.repeat_edge_style
        if edge.is_irregular_edge:
            return self.irregular_edge_style
        if edge.is_regular_edge:
            return self.regular_edge_style

    def get_pen_width(self, edge=None):
        if edge is None or not isinstance(edge, BGEdge):
            return self.regular_edge_pen_width
        if edge.is_repeat_edge:
            return self.repeat_edge_pen_width
        if edge.is_irregular_edge:
            return self.irregular_edge_pen_with
        if edge.is_regular_edge:
            return self.regular_edge_pen_width


class EdgeProcessor(object):
    def __init__(self, edge_shape_processor=None):
        self.edge_shape_processor = edge_shape_processor if edge_shape_processor is not None else EdgeShapeProcessor()
