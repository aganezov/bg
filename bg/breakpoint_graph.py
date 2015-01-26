# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"
from networkx import MultiGraph


class BreakpointGraph(object):
    def __init__(self):
        self.bg = MultiGraph()

    def add_edge(self, vertex1, vertex2, multicolor, *args, **kwargs):
        attr_dict = {"multicolor": multicolor}
        attr_dict.update(kwargs)
        self.bg.add_edge(u=vertex1, v=vertex2,
                         attr_dict=attr_dict)