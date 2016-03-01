# -*- coding: utf-8 -*-
from bg import BGVertex


class NodeShapeProcessor(object):
    def __init__(self):
        self.regular_vertex_shape = "oval"
        self.irregular_vertex_shape = "point"
        self.non_bg_vertex_shape = "oval"

    def get_shape(self, vertex=None):
        if isinstance(vertex, BGVertex):
            return self.regular_vertex_shape if vertex.is_regular_vertex else self.irregular_vertex_shape
        else:
            return self.non_bg_vertex_shape


class NodeTextProcessor(object):
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


class NodeProcessor(object):
    def __init__(self, shape_processor=None, text_processor=None):
        self.shape_processor = shape_processor if shape_processor is not None else NodeShapeProcessor()
        self.text_processor = text_processor if text_processor is not None else NodeTextProcessor()
