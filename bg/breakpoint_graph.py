# -*- coding: utf-8 -*-
from bg.multicolor import Multicolor

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"
from networkx import MultiGraph


class BreakpointGraph(object):
    def __init__(self):
        self.bg = MultiGraph()

    def add_edge(self, vertex1, vertex2, multicolor, *args, merge=True, **kwargs):
        attr_dict = {"multicolor": multicolor}
        attr_dict.update(kwargs)
        if self.bg.has_edge(u=vertex1, v=vertex2):
            if merge:
                self.bg[vertex1][vertex2][0]["multicolor"] += multicolor
                return
        self.bg.add_edge(u=vertex1, v=vertex2,
                         attr_dict=attr_dict)

    def split_edge(self, vertex1, vertex2, multicolor, guidance=None):
        if not self.bg.has_edge(v=vertex1, u=vertex2):
            raise ValueError("No edge to split between specified vertices")
        edge_to_split = None
        for edge in self.bg.edges(nbunch=vertex1):
            if edge[2]["multicolor"] == multicolor:
                edge_to_split = edge
                break
        else:
            raise ValueError("Noe edge to split with specified multicolor between specified vertices")
        if guidance is not None:
            pass
        else:
            for color in edge_to_split[2]["multicolor"].colors:
                self.add_edge(vertex1=edge_to_split[0],
                              vertex2=edge_to_split[1],
                              multicolor=Multicolor(color),
                              merge=False)
