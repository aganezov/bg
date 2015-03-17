# -*- coding: utf-8 -*-
from collections import Counter


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
        if not KBreak.valid_kbreak_matchings(start_edges=self.start_edges,
                                             result_edges=self.result_edges):
            raise ValueError("Supplied sets of start and result edges do not correspond to "
                             "correct k-break operation (either the set of vertices is not consistent, or "
                             "the degrees of vertices change)")

    @staticmethod
    def valid_kbreak_matchings(start_edges, result_edges):
        start_stats = Counter(vertex for vertex_pair in start_edges for vertex in vertex_pair)
        result_stats = Counter(vertex for vertex_pair in result_edges for vertex in vertex_pair)
        return start_stats == result_stats