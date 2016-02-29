# -*- coding: utf-8 -*-
from bg import BGVertex


class NodeShapeProcessor(object):
    def __init__(self):
        self.regular_vertex_shape = "circle"
        self.irregular_vertex_shape = "point"
        self.non_bg_vertex_shape = "circle"

    def get_shape(self, vertex=None):
        if isinstance(vertex, BGVertex):
            return self.regular_vertex_shape if vertex.is_regular_vertex else self.irregular_vertex_shape
        else:
            return self.non_bg_vertex_shape
