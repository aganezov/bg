# -*- coding: utf-8 -*-
from bg import BGVertex, BGEdge


class VertexShapeProcessor(object):
    def __init__(self, pen_width=1, regular_vertex_shape="oval", irregular_vertex_shape="point", non_bg_vertex_shape="oval"):
        self.pen_width = pen_width
        self.regular_vertex_shape = regular_vertex_shape
        self.irregular_vertex_shape = irregular_vertex_shape
        self.non_bg_vertex_shape = non_bg_vertex_shape

        self.pen_width_label = "penwidth"
        self.shape_label = "shape"

    def get_shape(self, vertex=None):
        if isinstance(vertex, BGVertex):
            return self.regular_vertex_shape if vertex.is_regular_vertex else self.irregular_vertex_shape
        else:
            return self.non_bg_vertex_shape

    def get_pen_width(self):
        return self.pen_width


class VertexTextProcessor(object):
    def __init__(self):
        self.text_color = "black"
        self.text_size = 12
        self.text_font_name = "Arial"

    def get_text_font(self):
        return self.text_font_name

    def get_text_size(self):
        return self.text_size

    def get_text_color(self):
        return self.text_color


class VertexProcessor(object):
    def __init__(self, shape_processor=None, text_processor=None):
        self.shape_processor = shape_processor if shape_processor is not None else VertexShapeProcessor()
        self.text_processor = text_processor if text_processor is not None else VertexTextProcessor()


class EdgeShapeProcessor(object):
    def __init__(self):
        self.regular_edge_style = "solid"
        self.irregular_edge_style = "dotted"
        self.repeat_edge_style = "dashed"
        self.regular_edge_pen_width = 1
        self.irregular_edge_pen_with = .1
        self.repeat_edge_pen_width = .5
        self.dir_type = "none"
        self.arrow_type = "none"

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

    def get_dir_type(self, edge=None):
        return self.dir_type


class EdgeProcessor(object):
    def __init__(self, edge_shape_processor=None):
        self.edge_shape_processor = edge_shape_processor if edge_shape_processor is not None else EdgeShapeProcessor()

