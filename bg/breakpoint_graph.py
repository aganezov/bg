# -*- coding: utf-8 -*-
from bg.edge import BGEdge
from bg.vertex import BGVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"
from networkx import MultiGraph


class BreakpointGraph(object):
    def __init__(self):
        self.bg = MultiGraph()

    def edges(self, nbunch=None):
        for v1, v2, data in self.bg.edges_iter(nbunch=nbunch, data=True):
            yield BGEdge(vertex1=v1, vertex2=v2, multicolor=data["multicolor"])

    def nodes(self):
        yield from self.bg.nodes_iter()

    def add_edge(self, vertex1, vertex2, multicolor):
        self.__add_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor))

    def __add_bgedge(self, bgedge):
        self.bg.add_edge(u=bgedge.vertex1, v=bgedge.vertex2, attr_dict={"multicolor": bgedge.multicolor})

    def add_bgedge(self, bgedge):
        self.__add_bgedge(bgedge=bgedge)

    def get_vertex_by_name(self, vertex_name):
        result = BGVertex(vertex_name)
        if result in self.bg.node:
            result.info = self.bg.node[result]
            return result

    def get_edge_by_two_vertices(self, vertex1, vertex2, key=0):
        if vertex1 in self.bg and vertex2 in self.bg[vertex1]:
            return BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=self.bg[vertex1][vertex2][key]["multicolor"])

    def get_edges_by_vertex(self, vertex):
        if vertex in self.bg:
            for vertex2, edges in self.bg[vertex].items():
                for _, data in self.bg[vertex][vertex2].items():
                    yield BGEdge(vertex1=vertex, vertex2=vertex2, multicolor=data["multicolor"])
