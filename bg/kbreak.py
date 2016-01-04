# -*- coding: utf-8 -*-
from collections import Counter


__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"


class KBreak(object):
    """ A generic object that can represent any k-break ( k>= 2)

    A notion of k-break arises from the bioinformatics combinatorial object BreakpointGraph and is first mentioned in http://home.gwu.edu/~maxal/ap_tcs08.pdf
    A generic k-break operates on k specified edges of spisific multicolor and replaces them with another set of k edges with the same multicolor on the same set of vertices in way, that the degree of vertices is kept intact.

    Initialization of the instance of :class:`KBreak` is performed with a validity check of supplied data, which must comply with the definition of k-break.

    Class carries following attributes carrying information about k-break structure:

    * :attr:`KBreak.start_edges`: a list of edges (in terms of paired vertices) that are to be removed by current :class:`KBreak`
    * :attr:`KBreak.result_edges`: a list of edges (in terms of paired vertices) that are to be created by current :class:`KBreak`
    * :attr:`KBreak.multicolor`: a :class:`bg.multicolor.Multicolor` instance, that specifies the multicolor of edges that are to be removed / created by current :class:`KBreak`

    Main operations:

    * :meth:`KBreak.valid_kbreak_matchings`: a method that checks if provided sets of started / resulted edges comply with the notions ob k-break definition
    """
    def __init__(self, start_edges, result_edges, multicolor, data=None):
        """ Initialization of :class:`KBreak` object.

        The initialization process consists of multiple checks, before any assignment and initialization itself is performed.

        First checks the fact, that information about start / result edges is supplied in form of paired vertices.
        Then check is performed to make sure, that degrees of vertices, that current :class:`KBreak` operates on, is preserved.

        :param start_edges: a list of pairs of vertices, that specifies where edges shall be removed by current :class:`KBreak`
        :type start_edges: ``list(tuple(vertex, vertex), ...)``
        :param result_edges: a list of pairs of vertices, that specifies where edges shall be created by current :class:`KBreak`
        :type result_edges: ``list(tuple(vertex, vertex), ...)``
        :param multicolor: a multicolor, that specifies which edges between specified pairs of vertices are to be removed / created
        :type multicolor: :class:`bg.multicolor.Multicolor`
        :return: a new instance of :class:`Kbreak`
        :rtype: :class:`KBreak`
        :raises: ``ValueError``
        """
        self.start_edges = start_edges
        self.result_edges = result_edges
        self.multicolor = multicolor
        if data is None:
            data = self.create_default_data_dict()
        self.data = data
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

    @property
    def is_a_two_break(self):
        return len(self.start_edges) == 2

    @property
    def is_a_fusion(self):
        return self.is_a_two_break and any(map(lambda vertex_set: all(map(lambda vertex: vertex.is_irregular_vertex, vertex_set)), self.result_edges))

    @classmethod
    def create_default_data_dict(cls):
        return {
            "origin": None
        }

    @staticmethod
    def valid_kbreak_matchings(start_edges, result_edges):
        """ A staticmethod check implementation that makes sure that degrees of vertices, that are affected by current :class:`KBreak`

        By the notion of k-break, it shall keep the degree of vertices in :class:`bg.breakpoint_graph.BreakpointGraph` the same, after its application.
        By utilizing the Counter class, such check is performed, as the number the vertex is mentioned corresponds to its degree.

        :param start_edges: a list of pairs of vertices, that specifies where edges shall be removed by :class:`KBreak`
        :type start_edges: ``list(tuple(vertex, vertex), ...)``
        :param result_edges: a list of pairs of vertices, that specifies where edges shall be created by :class:`KBreak`
        :type result_edges: ``list(tuple(vertex, vertex), ...)``
        :return: a flag indicating if the degree of vertices are equal in start / result edges, targeted by :class:`KBreak`
        :rtype: ``Boolean``
        """
        start_stats = Counter(vertex for vertex_pair in start_edges for vertex in vertex_pair)
        result_stats = Counter(vertex for vertex_pair in result_edges for vertex in vertex_pair)
        return start_stats == result_stats