# -*- coding: utf-8 -*-
from copy import deepcopy
from bg.edge import BGEdge
from bg.vertex import BGVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"
from networkx import MultiGraph
import networkx as nx


class BreakpointGraph(object):
    def __init__(self, graph=None):
        if graph is None:
            self.bg = MultiGraph()
        else:
            self.bg = graph

    def edges(self, nbunch=None):
        for v1, v2, data in self.bg.edges_iter(nbunch=nbunch, data=True):
            yield BGEdge(vertex1=v1, vertex2=v2, multicolor=data["multicolor"])

    def nodes(self):
        yield from self.bg.nodes_iter()

    def add_edge(self, vertex1, vertex2, multicolor):
        self.__add_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor))

    def __add_bgedge(self, bgedge):
        if bgedge.vertex1 in self.bg and bgedge.vertex2 in self.bg[bgedge.vertex1]:
            key = list(self.bg[bgedge.vertex1][bgedge.vertex2].keys())[0]
            self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"] += bgedge.multicolor
        else:
            self.bg.add_edge(u=bgedge.vertex1, v=bgedge.vertex2, attr_dict={"multicolor": deepcopy(bgedge.multicolor)})

    def add_bgedge(self, bgedge):
        self.__add_bgedge(bgedge=bgedge)

    def __get_vertex_by_name(self, vertex_name):
        result = BGVertex(vertex_name)
        if result in self.bg.node:
            result.info = self.bg.node[result]
            return result

    def get_vertex_by_name(self, vertex_name):
        return self.__get_vertex_by_name(vertex_name=vertex_name)

    def __get_edge_by_two_vertices(self, vertex1, vertex2, key=0):
        if vertex1 in self.bg and vertex2 in self.bg[vertex1]:
            return BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=self.bg[vertex1][vertex2][key]["multicolor"])

    def get_edge_by_two_vertices(self, vertex1, vertex2, key=0):
        return self.__get_edge_by_two_vertices(vertex1=vertex1, vertex2=vertex2, key=key)

    def get_edges_by_vertex(self, vertex):
        if vertex in self.bg:
            for vertex2, edges in self.bg[vertex].items():
                for _, data in self.bg[vertex][vertex2].items():
                    yield BGEdge(vertex1=vertex, vertex2=vertex2, multicolor=data["multicolor"])

    def connected_components_subgraphs(self, copy=True):
        for component in nx.connected_component_subgraphs(self.bg, copy=copy):
            yield BreakpointGraph(component)

    def __delete_bgedge(self, bgedge):
        internal_bgedge = self.__get_edge_by_two_vertices(vertex1=bgedge.vertex1, vertex2=bgedge.vertex2)
        if internal_bgedge is not None:
            internal_bgedge.multicolor -= bgedge.multicolor
            if len(internal_bgedge.multicolor.multicolors) == 0:
                self.bg.remove_edge(v=internal_bgedge.vertex1, u=bgedge.vertex2)

    def delete_edge(self, vertex1, vertex2, multicolor):
        self.__delete_bgedge(bgedge=BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor))

    def delete_bgedge(self, bgedge):
        self.__delete_bgedge(bgedge=bgedge)
