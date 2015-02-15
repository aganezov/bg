# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class BGEdge(object):
    def __init__(self, vertex1, vertex2, multicolor):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.multicolor = multicolor

    @staticmethod
    def merge(edge1, edge2):
        if edge1.vertex1 != edge2.vertex1 and edge1.vertex1 != edge2.vertex2:
            raise ValueError("Edges to be merged do not connect same vertices")
        forward = edge1.vertex1 == edge2.vertex1
        if forward and edge1.vertex2 != edge2.vertex2:
            raise ValueError("Edges to be merged do not connect same vertices")
        elif not forward and edge1.vertex2 != edge2.vertex1:
            raise ValueError("Edges to be merged do not connect same vertices")
        return BGEdge(vertex1=edge1.vertex1, vertex2=edge1.vertex2, multicolor=edge1.multicolor + edge2.multicolor)

    def __eq__(self, other):
        if not isinstance(other, BGEdge):
            return False
        if self.vertex1 != other.vertex1 and self.vertex1 != other.vertex2:
            return False
        multicolor_equality = self.multicolor == other.multicolor
        if self.vertex1 == other.vertex1:
            return self.vertex2 == other.vertex2 and multicolor_equality
        else:
            return self.vertex2 == other.vertex1 and multicolor_equality