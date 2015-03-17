# -*- coding: utf-8 -*-
from bg import BGEdge

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class KBreak(object):
    def __init__(self, start_edges, result_edges, multicolor):
        self.start_edges = start_edges
        self.result_edges = result_edges
        self.multicolor = multicolor
        for vertex_pair in self.start_edges:
            if len(vertex_pair) != 2:
                raise ValueError("Expected edges in a form of pairs of vertices.\n "
                                 "Not a pair of vertices ({issue}) in start edges."
                                 "".format(issue=str(vertex_pair)))
        for vertex_pair in self.result_edges:
            if len(vertex_pair) != 2:
                raise ValueError("Expected edges in a form of pairs of vertices.\n "
                                 "Not a pair of vertices ({issue}) in result edges."
                                 "".format(issue=str(vertex_pair)))