# -*- coding: utf-8 -*-
from copy import deepcopy
import itertools
from bg.edge import BGEdge
from bg.multicolor import Multicolor
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

    def __edges(self, nbunch=None):
        for v1, v2, data in self.bg.edges_iter(nbunch=nbunch, data=True):
            yield BGEdge(vertex1=v1, vertex2=v2, multicolor=data["multicolor"])

    def edges(self, nbunch=None):
        yield from self.__edges(nbunch=nbunch)

    def nodes(self):
        yield from self.bg.nodes_iter()

    def add_edge(self, vertex1, vertex2, multicolor, merge=True):
        self.__add_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor), merge=merge)

    def __add_bgedge(self, bgedge, merge=True):
        if bgedge.vertex1 in self.bg and bgedge.vertex2 in self.bg[bgedge.vertex1] and merge:
            key = min(self.bg[bgedge.vertex1][bgedge.vertex2].keys())
            self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"] += bgedge.multicolor
        else:
            self.bg.add_edge(u=bgedge.vertex1, v=bgedge.vertex2, attr_dict={"multicolor": deepcopy(bgedge.multicolor)})

    def add_bgedge(self, bgedge, merge=True):
        self.__add_bgedge(bgedge=bgedge, merge=merge)

    def __get_vertex_by_name(self, vertex_name):
        result = BGVertex(vertex_name)
        if result in self.bg.node:
            result.info = self.bg.node[result]
            return result

    def get_vertex_by_name(self, vertex_name):
        return self.__get_vertex_by_name(vertex_name=vertex_name)

    def __get_edge_by_two_vertices(self, vertex1, vertex2, key=None):
        if vertex1 in self.bg and vertex2 in self.bg[vertex1]:
            if key is None:
                key = min(self.bg[vertex1][vertex2])
            return BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=self.bg[vertex1][vertex2][key]["multicolor"])

    def get_edge_by_two_vertices(self, vertex1, vertex2, key=None):
        return self.__get_edge_by_two_vertices(vertex1=vertex1, vertex2=vertex2, key=key)

    def __get_edges_by_vertex(self, vertex):
        if vertex in self.bg:
            for vertex2, edges in self.bg[vertex].items():
                for _, data in self.bg[vertex][vertex2].items():
                    yield BGEdge(vertex1=vertex, vertex2=vertex2, multicolor=data["multicolor"])

    def get_edges_by_vertex(self, vertex):
        yield from self.__get_edges_by_vertex(vertex=vertex)

    def connected_components_subgraphs(self, copy=True):
        for component in nx.connected_component_subgraphs(self.bg, copy=copy):
            yield BreakpointGraph(component)

    def __delete_bgedge(self, bgedge, key=None):
        candidate_id = None
        candidate_score = -1
        candidate_data = None
        if key is not None:
            self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"] -= bgedge.multicolor
            if len(self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"].multicolors) == 0:
                self.bg.remove_edge(v=bgedge.vertex1, u=bgedge.vertex2, key=key)
        else:
            for v1, v2, key, data in self.bg.edges_iter(nbunch=bgedge.vertex1, data=True, keys=True):
                if v2 == bgedge.vertex2:
                    score = Multicolor.similarity_score(bgedge.multicolor, data["multicolor"])
                    if score > candidate_score:
                        candidate_id = key
                        candidate_data = data
                        candidate_score = score
            if candidate_data is not None:
                candidate_data["multicolor"] -= bgedge.multicolor
                if len(self.bg[bgedge.vertex1][bgedge.vertex2][candidate_id]["multicolor"].multicolors) == 0:
                    self.bg.remove_edge(v=bgedge.vertex1, u=bgedge.vertex2, key=candidate_id)

    def delete_edge(self, vertex1, vertex2, multicolor, key=None):
        self.__delete_bgedge(bgedge=BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor), key=key)

    def delete_bgedge(self, bgedge, key=None):
        self.__delete_bgedge(bgedge=bgedge, key=key)

    def __split_bgedge(self, bgedge, guidance=None, duplication_splitting=False, key=None):
        candidate_id = None
        candidate_score = 0
        candidate_data = None
        if key is not None:
            new_multicolors = Multicolor.split_colors(
                multicolor=self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"], guidance=guidance)
            self.__delete_bgedge(bgedge=BGEdge(vertex1=bgedge.vertex1, vertex2=bgedge.vertex2,
                                               multicolor=self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"]),
                                 key=key)
            for multicolor in new_multicolors:
                self.__add_bgedge(BGEdge(vertex1=bgedge.vertex1, vertex2=bgedge.vertex2, multicolor=multicolor),
                                  merge=False)
        else:
            for v1, v2, key, data in self.bg.edges_iter(nbunch=bgedge.vertex1, data=True, keys=True):
                if v2 == bgedge.vertex2:
                    score = Multicolor.similarity_score(bgedge.multicolor, data["multicolor"])
                    if score > candidate_score:
                        candidate_id = key
                        candidate_data = data
                        candidate_score = score
            if candidate_data is not None:
                new_multicolors = Multicolor.split_colors(multicolor=candidate_data["multicolor"], guidance=guidance)
                self.__delete_bgedge(bgedge=BGEdge(vertex1=bgedge.vertex1, vertex2=bgedge.vertex2,
                                                   multicolor=candidate_data["multicolor"]),
                                     key=candidate_id)
                for multicolor in new_multicolors:
                    self.__add_bgedge(BGEdge(vertex1=bgedge.vertex1, vertex2=bgedge.vertex2,
                                             multicolor=multicolor), merge=False)

    def split_edge(self, vertex1, vertex2, multicolor, guidance=None, duplication_splitting=False, key=None):
        self.__split_bgedge(bgedge=BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor), guidance=guidance,
                            duplication_splitting=duplication_splitting, key=key)

    def split_bgedge(self, bgedge, guidance=None, duplication_splitting=False, key=None):
        self.__split_bgedge(bgedge=bgedge, guidance=guidance, duplication_splitting=duplication_splitting,
                            key=key)

    def __split_all_edges_between_two_vertices(self, vertex1, vertex2, guidance=None):
        edges_to_be_split_keys = [key for v1, v2, key in self.bg.edges_iter(nbunch=vertex1, keys=True) if v2 == vertex2]
        for key in edges_to_be_split_keys:
            self.__split_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=None), guidance=guidance, key=key)

    def split_all_edges_between_two_vertices(self, vertex1, vertex2, guidance=None):
        self.__split_all_edges_between_two_vertices(vertex1=vertex1, vertex2=vertex2, guidance=guidance)

    def split_all_edges(self, guidance=None):
        for v1, v2 in itertools.combinations(self.bg.nodes_iter(), 2):
            self.__split_all_edges_between_two_vertices(vertex1=v1, vertex2=v2, guidance=guidance)

    def __delete_all_bgedges_between_two_vertices(self, vertex1, vertex2):
        edges_to_be_split_keys = [(key, data) for v1, v2, key, data in self.bg.edges_iter(nbunch=vertex1, keys=True,
                                                                                          data=True) if v2 == vertex2]
        for key, data in edges_to_be_split_keys:
            self.__delete_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=data["multicolor"]), key=key)

    def delete_all_edges_between_two_vertices(self, vertex1, vertex2):
        self.__delete_all_bgedges_between_two_vertices(vertex1=vertex1, vertex2=vertex2)

    def __merge_all_bgedges_between_two_vertices(self, vertex1, vertex2):
        edges_multicolors = [deepcopy(data["multicolor"]) for v1, v2, data in
                             self.bg.edges_iter(nbunch=vertex1, data=True) if v2 == vertex2]
        self.__delete_all_bgedges_between_two_vertices(vertex1=vertex1, vertex2=vertex2)
        for multicolor in edges_multicolors:
            self.__add_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor), merge=True)

    def merge_all_edges_between_two_vertices(self, vertex1, vertex2):
        self.__merge_all_bgedges_between_two_vertices(vertex1=vertex1, vertex2=vertex2)

    def merge_all_edges(self):
        for v1, v2 in itertools.combinations(self.bg.nodes_iter(), 2):
            self.__merge_all_bgedges_between_two_vertices(vertex1=v1, vertex2=v2)

    @staticmethod
    def merge(breakpoint_graph1, breakpoint_graph2, merge_edges=False):
        result = BreakpointGraph()
        for bgedge in breakpoint_graph1.edges():
            result.__add_bgedge(bgedge=bgedge, merge=merge_edges)
        for bgedge in breakpoint_graph2.edges():
            result.__add_bgedge(bgedge=bgedge, merge=merge_edges)
        return result

    def __update(self, breakpoint_graph, merge_edges=False):
        for bgedge in breakpoint_graph.edges():
            self.__add_bgedge(bgedge=bgedge, merge=merge_edges)

    def update(self, breakpoint_graph, merge_edges=False):
        self.__update(breakpoint_graph=breakpoint_graph,
                      merge_edges=merge_edges)