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
    """ Class providing implementation of breakpoint graph data structure and most utilized operations on it.

    :class:`BreakpointGraph` anticipates to work with :class:`bg.vertex.BGVertex`, :class:`bg.edge.BGEdge` and :class:`bg.multicolor.Multicolor` classes instances, but is not limited to them. Extreme caution has to be assumed when working with non-expected classes.



    The engine of graph information storage, low-level algorithms implementation is powered by NetworkX package MultiGraph data structure. This class provides a smart wrapping around it to perform most useful, from combinatorial bioinformatics stand point, operations and manipulations.

    Class carries following attributes carrying information about graphs structure:

    *   :attr:`BreakpointGraph.bg`: instance of NetworkX MultiGraph class

    Main operations:

    *   :meth:`BreakpointGraph.add_bgedge`: adds an instance of :class:`bg.edge.BGEdge` to the current :class:`BreakpointGraph`
    *   :meth:`BreakpointGraph.add_edge`: adds a new :class:`bg.edge.BGEdge`, constructed from a pair of supplied vertices instances and :class:`bg.multicolor.Multicolor` object, to the current :class:`BreakpointGraph`
    *   :meth:`BreakpointGraph.get_vertex_by_name`: returns a :class:`bg.vertex.BGVertex` instance by provided ``name`` argument
    *   :meth:`BreakpointGraph.get_edge_by_two_vertices`: returns a first edge (order is determined by ``key`` NetworkX MultiGraph edge attribute) between two supplied :class:`bg.vertex.BGVertex`
    *   :meth:`BreakpointGraph.get_edges_by_vertex`: returns a generator yielding :class:`bg.edge.BGEdge`
    *   :meth:`BreakpointGraph.connected_components_subgraphs`: returns a generator of :class:`BreakpointGraph` object, that represent connected components of a current :class:`BreakpointGraph` object, deep copying(by default) all information of current :class:`BreakpointGraph`
    *   :meth:`BreakpointGraph.delete_edge`: deletes and edge from perspective of multi-color substitution of supplied vertices
    *   :meth:`BreakpointGraph.delete_bgedge`: deletes a supplied :class:`bg.edge.BGEdge` instance from perspective of substituting multi-colors.
    *   :meth:`BreakpointGraph.split_edge`: deletes a supplied :class:`bg.multicolor.Multicolor` instance in identifies edge from two supplied vertices.
    *   :meth:`BreakpointGraph.split_bgedge`: splits a :class:`bg.edge.BGEdge` with respect to provided guidance
    *   :meth:`BreakpointGraph.split_all_edges_between_two_vertices`: splits all edges between two supplied vertives with respect to provided guidance.
    *   :meth:`BreakpointGraph.split_all_edges`: splits all edge in :class:`BreakpointGraph` with respect to provided guidance.
    *   :meth:`BreakpointGraph.delete_all_edges_between_two_vertices`: deletes all edges between two given vertices, by plain deleting them from MultiGraph underling structure.
    *   :meth:`BreakpointGraph.merge_all_edges_between_two_vertices`: merges all edge between two given vertices creating a single edge containing information about multi-colors in respective edges.
    *   :meth:`BreakpointGraph.merge_all_edges`: merges all edges in current :class:`BreakpointGraph`.
    *   :meth:`BreakpointGraph.merge`: merges two :class:`BreakpointGraph` instances with respect to vertices, edges, and multicolors.
    *   :meth:`BreakpointGraph.update`: updates information in current :class:`BreakpointGraph` instance by adding new :class:`bg.edge.BGEdge` instances form supplied :class:`BreakpointGraph`.
    """
    def __init__(self, graph=None):
        """ Initialization of a :class:`BreakpointGraph` object.



        :param graph: is supplied, :class:`BreakpointGraph` is initialized with supplied or brand new (empty) instance of NetworkX MultiGraph.
        :type graph: instance of NetworkX MultiGraph is expected.
        :return: ``None``, performs initialization of respective instance of :class:`BreakpointGraph`
        """
        if graph is None:
            self.bg = MultiGraph()
        else:
            self.bg = graph

    def __edges(self, nbunch=None):
        """ Iterates over edges in current :class:`BreakpointGraph` instance.

        Returns a generator over the edges in current :class:`BreakpointGraph` instance producing instances of :class:`bg.edge.BGEdge` instances wrapping around information in underlying MultiGraph object.

        :param nbunch: a vertex to iterate over edges outgoing from, if not provided,iteration over all edges is performed.
        :type nbuch: any hashable python object
        :return: generator over edges in current :class:`BreakpointGraph`
        :rtype: ``generator``
        """
        for v1, v2, data in self.bg.edges_iter(nbunch=nbunch, data=True):
            yield BGEdge(vertex1=v1, vertex2=v2, multicolor=data["multicolor"])

    def edges(self, nbunch=None):
        """ Iterates over edges in current :class:`BreakpointGraph` instance.

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__edges`.

        :param nbunch: a vertex to iterate over edges outgoing from, if not provided,iteration over all edges is performed.
        :type nbuch: any hashable python object
        :return: generator over edges in current :class:`BreakpointGraph`
        :rtype: ``generator``
        """
        yield from self.__edges(nbunch=nbunch)

    def nodes(self):
        """ Iterates over nodes in current :class:`BreakpointGraph` instance.

        :return:  generator over nodes (vertices) in current :class:`BreakpointGraph` instance.
        :rtype: ``generator``
        """
        yield from self.bg.nodes_iter()

    def add_edge(self, vertex1, vertex2, multicolor, merge=True):
        """ Creates a new :class:`bg.edge.BGEdge` object from supplied information and adds it to current instance of :class:`BreakpointGraph`.

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__add_bgedge` method.

        :param vertex1: first vertex instance out of two in current :class:`BreakpointGraph`
        :type vertex1: any hashable object
        :param vertex2: second vertex instance out of two in current :class:`BreakpointGraph`
        :type vertex2: any hashable object
        :param multicolor: an information about multi-colors of added edge
        :type multicolor: :class:`bg.multicolor.Multicolor`
        :param merge: a flag to merge supplied information from multi-color perspective into a first existing edge between two supplied vertices
        :type merge: ``Boolean``
        :return: ``None``, performs inplace changes
        """
        self.__add_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor), merge=merge)

    def __add_bgedge(self, bgedge, merge=True):
        """ Adds supplied :class:`bg.edge.BGEdge` object to current instance of :class:`BreakpointGraph`.

        Checks that vertices in supplied :class:`bg.edge.BGEdge` instance actually are present in current :class:`BreakpointGraph` if **merge** option of provided. Otherwise a new edge is added to the current :class:`BreakpointGraph`.

        :param bgedge: instance of :class:`bg.edge.BGEdge` infromation form which is to be added to current :class:`BreakpointGraph`
        :type bgedge: :class:`bg.edge.BGEdge`
        :param merge: a flag to merge supplied information from multi-color perspective into a first existing edge between two supplied vertices
        :type merge: ``Boolean``
        :return: ``None``, performs inplace changes
        """
        if bgedge.vertex1 in self.bg and bgedge.vertex2 in self.bg[bgedge.vertex1] and merge:
            key = min(self.bg[bgedge.vertex1][bgedge.vertex2].keys())
            self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"] += bgedge.multicolor
        else:
            self.bg.add_edge(u=bgedge.vertex1, v=bgedge.vertex2, attr_dict={"multicolor": deepcopy(bgedge.multicolor)})

    def add_bgedge(self, bgedge, merge=True):
        """ Adds supplied :class:`bg.edge.BGEdge` object to current instance of :class:`BreakpointGraph`.

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__add_bgedge` method.

        :param bgedge: instance of :class:`bg.edge.BGEdge` infromation form which is to be added to current :class:`BreakpointGraph`
        :type bgedge: :class:`bg.edge.BGEdge`
        :param merge: a flag to merge supplied information from multi-color perspective into a first existing edge between two supplied vertices
        :type merge: ``Boolean``
        :return: ``None``, performs inplace changes
        """
        self.__add_bgedge(bgedge=bgedge, merge=merge)

    def __get_vertex_by_name(self, vertex_name):
        """ Obtains a vertex object by supplied label

        Returns a :class:`bg.vertex.BGVertex` instance with supplied label as :attr:`bg.vertex.BGVertex.name` is present in current :class:`BreakpointGraph`.

        :param vertex_name: a vertex label it is identified by.
        :type vertex_name: any hashable python object. ``str`` expected.
        :return: vertex with supplied label if present in current :class:`BreakpointGraph`, ``None`` otherwise
        :rtype: :class:`bg.vertex.BGVertex` or ``None``
        """
        result = BGVertex(vertex_name)
        if result in self.bg.node:
            result.info = self.bg.node[result]
            return result

    def get_vertex_by_name(self, vertex_name):
        """ Obtains a vertex object by supplied label

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__get_vertex_by_name`.

        :param vertex_name: a vertex label it is identified by.
        :type vertex_name: any hashable python object. ``str`` expected.
        :return: vertex with supplied label if present in current :class:`BreakpointGraph`, ``None`` otherwise
        :rtype: :class:`bg.vertex.BGVertex` or ``None``
        """
        return self.__get_vertex_by_name(vertex_name=vertex_name)

    def __get_edge_by_two_vertices(self, vertex1, vertex2, key=None):
        """ Returns an instance of :class:`bg.edge.BBGEdge` edge between to supplied vertices (if ``key`` is supplied, returns a :class:`bg.edge.BBGEdge` instance about specified edge).

        Checks that both specified vertices are in current :class:`BreakpointGraph` and then depending on ``key`` argument, creates a new :class:`bg.edge.BBGEdge` instance and incorporates respective multi-color information into it.

        :param vertex1: first vertex instance out of two in current :class:`BreakpointGraph`
        :type vertex1: any hashable object
        :param vertex2: second vertex instance out of two in current :class:`BreakpointGraph`
        :type vertex2: any hashable object
        :param key: unique identifier of edge of interested to be retrieved from current :class:`BreakpointGraph`
        :type key: any python object. ``None`` or ``int`` is expected
        :return: edge between two specified edges respecting a ``key`` argument.
        :rtype: :class:`bg.edge.BGEdge`
        """
        if vertex1 in self.bg and vertex2 in self.bg[vertex1]:
            if key is None:
                key = min(self.bg[vertex1][vertex2])
            return BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=self.bg[vertex1][vertex2][key]["multicolor"])

    def get_edge_by_two_vertices(self, vertex1, vertex2, key=None):
        """ Returns an instance of :class:`bg.edge.BBGEdge` edge between to supplied vertices (if ``key`` is supplied, returns a :class:`bg.edge.BBGEdge` instance about specified edge).

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__get_edge_by_two_vertices`.

        :param vertex1: first vertex instance out of two in current :class:`BreakpointGraph`
        :type vertex1: any hashable object
        :param vertex2: second vertex instance out of two in current :class:`BreakpointGraph`
        :type vertex2: any hashable object
        :param key: unique identifier of edge of interested to be retrieved from current :class:`BreakpointGraph`
        :type key: any python object. ``None`` or ``int`` is expected
        :return: edge between two specified edges respecting a ``key`` argument.
        :rtype: :class:`bg.edge.BGEdge`
        """
        return self.__get_edge_by_two_vertices(vertex1=vertex1, vertex2=vertex2, key=key)

    def __get_edges_by_vertex(self, vertex):
        """ Iterates over edges that are incident to supplied vertex argument in current :class:`BreakpointGraph`

        Checks that the supplied vertex argument exists in underlying MultiGraph object as a vertex, then iterates over all edges that are incident to it. Wraps each yielded object into :class:`bg.edge.BGEdge` object.

        :param vertex: a vertex object in current :class:`BreakpointGraph` object
        :type vertex: any hashable object. :class:`bg.vertex.BGVertex` object is expected.
        :return: generator over edges in current :class:`BreakpointGraph` wrapped in :class:`bg.vertex.BGEVertex`
        :rtype: ``generator``
        """
        if vertex in self.bg:
            for vertex2, edges in self.bg[vertex].items():
                for _, data in self.bg[vertex][vertex2].items():
                    yield BGEdge(vertex1=vertex, vertex2=vertex2, multicolor=data["multicolor"])

    def get_edges_by_vertex(self, vertex):
        """ Iterates over edges that are incident to supplied vertex argument in current :class:`BreakpointGraph`

        Proxies a call to :meth:`Breakpoint._Breakpoint__get_edges_by_vertex` method.

        :param vertex: a vertex object in current :class:`BreakpointGraph` object
        :type vertex: any hashable object. :class:`bg.vertex.BGVertex` object is expected.
        :return: generator over edges in current :class:`BreakpointGraph` wrapped in :class:`bg.vertex.BGEVertex`
        :rtype: ``generator``
        """
        yield from self.__get_edges_by_vertex(vertex=vertex)

    def connected_components_subgraphs(self, copy=True):
        """ Iterates over connected components in current :class:`BreakpointGraph` object, and yields new instances of :class:`BreakpointGraph` with respective information deep-copied by default (week reference is possible of specified in method call).

        :param copy: a flag to signal if graph information has to be deep copied while producing new :class:`BreakpointGraph` instances, of just reference to respective data has to be made.
        :type copy: ``Boolean``
        :return: generator over connected components in current :class:`BreakpointGraph` wrapping respective connected components into new :class:`BreakpointGraph` objects.
        :rtype: ``generator``
        """
        for component in nx.connected_component_subgraphs(self.bg, copy=copy):
            yield BreakpointGraph(component)

    def __delete_bgedge(self, bgedge, key=None):
        """ Deletes a supplied :class:`bg.edge.BGEdge` from a perspective of multi-color substitution. If unique identifier ``key`` is not provided, most similar (from perspective of :meth:`bg.multicolor.Multicolor.similarity_score` result) edge between respective vertices is chosen for change.

        If no unique identifier for edge to be changed is specified, edge to be updated is determined by iterating over all edges between vertices in supplied :class:`bg.edge.BGEdge` instance and the edge with most similarity score to supplied one is chosen.
        Once the edge to be substituted from is determined, substitution if performed form a perspective of :class:`bg.multicolor.Multicolor` substitution.
        If after substitution the remaining multicolor of respective edge is empty, such edge is deleted form a perspective of MultiGraph edge deletion.

        :param bgedge: an edge to be deleted from a perspective of multi-color substitution
        :type bgedge: :class:`bg.edge.BGEdge`
        :param key: unique identifier of existing edges in current :class:`BreakpointGraph` instance to be changed
        :type: any python object. ``int`` is expected.
        :return: ``None``, performed inplace changes.
        """
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
        """ Creates a new :class:`bg.edge.BGEdge` instance from supplied information and deletes it from a perspective of multi-color substitution. If unique identifier ``key`` is not provided, most similar (from perspective of :meth:`bg.multicolor.Multicolor.similarity_score` result) edge between respective vertices is chosen for change.

        Proxies a call to :math:`BreakpointGraph._BreakpointGraph__delete_bgedge` method.

        :param vertex1: a first vertex out of two the edge to be deleted is incident to
        :type vertex1: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second vertex out of two the edge to be deleted is incident to
        :type vertex2: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param multicolor: a multi-color to find most suitable edge to be deleted
        :type multicolor: :class:`bg.multicolor.Multicolor`
        :param key: unique identifier of existing edges in current :class:`BreakpointGraph` instance to be changed
        :type: any python object. ``int`` is expected.
        :return: ``None``, performed inplace changes.
        """
        self.__delete_bgedge(bgedge=BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor), key=key)

    def delete_bgedge(self, bgedge, key=None):
        """ Deletes a supplied :class:`bg.edge.BGEdge` from a perspective of multi-color substitution. If unique identifier ``key`` is not provided, most similar (from perspective of :meth:`bg.multicolor.Multicolor.similarity_score` result) edge between respective vertices is chosen for change.

        Proxies a call to :math:`BreakpointGraph._BreakpointGraph__delete_bgedge` method.

        :param bgedge: an edge to be deleted from a perspective of multi-color substitution
        :type bgedge: :class:`bg.edge.BGEdge`
        :param key: unique identifier of existing edges in current :class:`BreakpointGraph` instance to be changed
        :type: any python object. ``int`` is expected.
        :return: ``None``, performed inplace changes.
        """
        self.__delete_bgedge(bgedge=bgedge, key=key)

    def __split_bgedge(self, bgedge, guidance=None, duplication_splitting=False, key=None):
        """ Splits a :class:`bg.edge.BGEdge` in current :class:`BreakpointGraph` most similar to supplied one (if no unique identifier ``key`` is provided) with respect to supplied guidance.

        If no unique identifier for edge to be changed is specified, edge to be split is determined by iterating over all edges between vertices in supplied :class:`bg.edge.BGEdge` instance and the edge with most similarity score to supplied one is chosen.
        Once the edge to be split is determined, split if performed form a perspective of :class:`bg.multicolor.Multicolor` split.
        The originally detected edge is deleted, and new edges containing information about multi-colors after splitting, are added to the current :class:`BreakpointGraph`.


        :param bgedge: an edge to find most "similar to" among existing edges for a split
        :type bgedge: :class:`bg.edge.BGEdge`
        :param guidance: a guidance for underlying :class:`bg.multicolor.Multicolor` object to be split
        :type guidance: iterable where each entry is iterable with colors entries
        :param duplication_splitting: flag (**not** currently implemented) for a splitting of color-based splitting to take into account multiplicity of respective colors
        :type duplication_splitting: ``Boolean``
        :param key: unique identifier of edge to be split
        :type key: any python object. ``int`` is expected
        :return: ``None``, performs inplace changes
        """
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
        """ Splits an edge in current :class:`BreakpointGraph` most similar to supplied data (if no unique identifier ``key`` is provided) with respect to supplied guidance.

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__split_bgedge` method.

        :param vertex1: a first vertex out of two the edge to be split is incident to
        :type vertex1: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second vertex out of two the edge to be split is incident to
        :type vertex2: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param multicolor: a multi-color to find most suitable edge to be split
        :type multicolor: :class:`bg.multicolor.Multicolor`
        :param duplication_splitting: flag (**not** currently implemented) for a splitting of color-based splitting to take into account multiplicity of respective colors
        :type duplication_splitting: ``Boolean``
        :param key: unique identifier of edge to be split
        :type key: any python object. ``int`` is expected
        :return: ``None``, performs inplace changes
        """
        self.__split_bgedge(bgedge=BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor), guidance=guidance,
                            duplication_splitting=duplication_splitting, key=key)

    def split_bgedge(self, bgedge, guidance=None, duplication_splitting=False, key=None):
        """ Splits a :class:`bg.edge.BGEdge` in current :class:`BreakpointGraph` most similar to supplied one (if no unique identifier ``key`` is provided) with respect to supplied guidance.

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__split_bgedge` method.

        :param bgedge: an edge to find most "similar to" among existing edges for a split
        :type bgedge: :class:`bg.edge.BGEdge`
        :param guidance: a guidance for underlying :class:`bg.multicolor.Multicolor` object to be split
        :type guidance: iterable where each entry is iterable with colors entries
        :param duplication_splitting: flag (**not** currently implemented) for a splitting of color-based splitting to take into account multiplicity of respective colors
        :type duplication_splitting: ``Boolean``
        :param key: unique identifier of edge to be split
        :type key: any python object. ``int`` is expected
        :return: ``None``, performs inplace changes
        """
        self.__split_bgedge(bgedge=bgedge, guidance=guidance, duplication_splitting=duplication_splitting,
                            key=key)

    def __split_all_edges_between_two_vertices(self, vertex1, vertex2, guidance=None):
        """ Splits all edges between two supplied vertices in current :class:`BreakpointGraph` instance with respect to the provided guidance.

        Iterates over all edges between two supplied vertices and splits each one of them with respect to the guidance.

        :param vertex1: a first out of two vertices edges between which are to be split
        :type vertex1: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second out of two vertices edges between which are to be split
        :type vertex2: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param guidance: a guidance for underlying :class:`bg.multicolor.Multicolor` objects to be split
        :type guidance: iterable where each entry is iterable with colors entries
        :return: ``None``, performs inplace changes
        """
        edges_to_be_split_keys = [key for v1, v2, key in self.bg.edges_iter(nbunch=vertex1, keys=True) if v2 == vertex2]
        for key in edges_to_be_split_keys:
            self.__split_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=None), guidance=guidance, key=key)

    def split_all_edges_between_two_vertices(self, vertex1, vertex2, guidance=None):
        """ Splits all edges between two supplied vertices in current :class:`BreakpointGraph` instance with respect to the provided guidance.

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__split_all_edges_between_two_vertices` method.

        :param vertex1: a first out of two vertices edges between which are to be split
        :type vertex1: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second out of two vertices edges between which are to be split
        :type vertex2: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param guidance: a guidance for underlying :class:`bg.multicolor.Multicolor` objects to be split
        :type guidance: iterable where each entry is iterable with colors entries
        :return: ``None``, performs inplace changes
        """
        self.__split_all_edges_between_two_vertices(vertex1=vertex1, vertex2=vertex2, guidance=guidance)

    def split_all_edges(self, guidance=None):
        """ Splits all edge in current :class:`BreakpointGraph` instance with respect to the provided guidance.

        Iterate over all possible distinct pairs of vertices in current :class:`BreakpointGraph` instance and splits all edges between such pairs with respect to provided guidance.

        :param guidance: a guidance for underlying :class:`bg.multicolor.Multicolor` objects to be split
        :type guidance: iterable where each entry is iterable with colors entries
        :return: ``None``, performs inplace changes
        """
        for v1, v2 in itertools.combinations(self.bg.nodes_iter(), 2):
            self.__split_all_edges_between_two_vertices(vertex1=v1, vertex2=v2, guidance=guidance)

    def __delete_all_bgedges_between_two_vertices(self, vertex1, vertex2):
        """ Deletes all edges between two supplied vertices

        :param vertex1: a first out of two vertices edges between which are to be deleted
        :type vertex1: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second out of two vertices edges between which are to be deleted
        :type vertex2: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :return: ``None``, performs inplace changes
        """
        edges_to_be_split_keys = [(key, data) for v1, v2, key, data in self.bg.edges_iter(nbunch=vertex1, keys=True,
                                                                                          data=True) if v2 == vertex2]
        for key, data in edges_to_be_split_keys:
            self.__delete_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=data["multicolor"]), key=key)

    def delete_all_edges_between_two_vertices(self, vertex1, vertex2):
        """ Deletes all edges between two supplied vertices

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__delete_all_bgedges_between_two_vertices` method.

        :param vertex1: a first out of two vertices edges between which are to be deleted
        :type vertex1: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second out of two vertices edges between which are to be deleted
        :type vertex2: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :return: ``None``, performs inplace changes
        """
        self.__delete_all_bgedges_between_two_vertices(vertex1=vertex1, vertex2=vertex2)

    def __merge_all_bgedges_between_two_vertices(self, vertex1, vertex2):
        """ Merges all edge between two supplied vertices into a single edge from a perspective of multi-color merging.

        :param vertex1: a first out of two vertices edges between which are to be merged together
        :type vertex1: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second out of two vertices edges between which are to be merged together
        :type vertex2: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :return: ``None``, performs inplace changes
        """
        edges_multicolors = [deepcopy(data["multicolor"]) for v1, v2, data in
                             self.bg.edges_iter(nbunch=vertex1, data=True) if v2 == vertex2]
        self.__delete_all_bgedges_between_two_vertices(vertex1=vertex1, vertex2=vertex2)
        for multicolor in edges_multicolors:
            self.__add_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor), merge=True)

    def merge_all_edges_between_two_vertices(self, vertex1, vertex2):
        """ Merges all edge between two supplied vertices into a single edge from a perspective of multi-color merging.

         Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__merge_all_bgedges_between_two_vertices`

        :param vertex1: a first out of two vertices edges between which are to be merged together
        :type vertex1: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second out of two vertices edges between which are to be merged together
        :type vertex2: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :return: ``None``, performs inplace changes
        """
        self.__merge_all_bgedges_between_two_vertices(vertex1=vertex1, vertex2=vertex2)

    def merge_all_edges(self):
        """ Merges all edges in a current :class`BreakpointGraph` instance between same pairs of vertices into a single edge from a perspective of multi-color merging.

        Iterates over all possible pairs of vertices in current :class:`BreakpointGraph` and merges all edges between respective pairs.

        :return: ``None``, performs inplace changes
        """
        for v1, v2 in itertools.combinations(self.bg.nodes_iter(), 2):
            self.__merge_all_bgedges_between_two_vertices(vertex1=v1, vertex2=v2)

    @staticmethod
    def merge(breakpoint_graph1, breakpoint_graph2, merge_edges=False):
        """ Merges two given instances of :class`BreakpointGraph` into a new one, that gather all available information from both supplied objects.

        Depending of a ``merge_edges`` flag, while merging of two dat structures is occurring, edges between similar vertices can be merged during the creation of a result :class`BreakpointGraph` obejct.

        :param breakpoint_graph1: a first out of two :class`BreakpointGraph` instances to gather information from
        :type breakpoint_graph1: :class`BreakpointGraph`
        :param breakpoint_graph2: a second out of two :class`BreakpointGraph` instances to gather information from
        :type breakpoint_graph2: :class`BreakpointGraph`
        :param merge_edges: flag to indicate if edges in a new merged :class`BreakpointGraph` object has to be merged between same vertices, or if splitting from supplied graphs shall be preserved.
        :type merge_edges: ``Boolean``
        :return: a new breakpoint graph object that contains all information gathered from both supplied breakpoint graphs
        :rtype: :class`BreakpointGraph`
        """
        result = BreakpointGraph()
        for bgedge in breakpoint_graph1.edges():
            result.__add_bgedge(bgedge=deepcopy(bgedge), merge=merge_edges)
        for bgedge in breakpoint_graph2.edges():
            result.__add_bgedge(bgedge=deepcopy(bgedge), merge=merge_edges)
        return result

    def __update(self, breakpoint_graph, merge_edges=False):
        """ Updates a current :class`BreakpointGraph` object with information from a supplied :class`BreakpointGraph` instance.

        Depending of a ``merge_edges`` flag, while updating of a current :class`BreakpointGraph` object is occuring, edges between similar vertices can be merged to already existing ones.

        :param breakpoint_graph: a breakpoint graph to extract information from, which will be then added to the current
        :type breakpoint_graph: :class`BreakpointGraph`
        :param merge_edges: flag to indicate if edges to be added to current :class`BreakpointGraph` object are to be merged to already existing ones
        :type merge_edges: ``Boolean``
        :return: ``None``, performs inplace changes
        """
        for bgedge in breakpoint_graph.edges():
            self.__add_bgedge(bgedge=deepcopy(bgedge), merge=merge_edges)

    def update(self, breakpoint_graph, merge_edges=False):
        """ Updates a current :class`BreakpointGraph` object with information from a supplied :class`BreakpointGraph` instance.

        Proxoes a call to :meth:`BreakpointGraph._BreakpointGraph__update` method.

        :param breakpoint_graph: a breakpoint graph to extract information from, which will be then added to the current
        :type breakpoint_graph: :class:`BreakpointGraph`
        :param merge_edges: flag to indicate if edges to be added to current :class`BreakpointGraph` object are to be merged to already existing ones
        :type merge_edges: ``Boolean``
        :return: ``None``, performs inplace changes
        """
        self.__update(breakpoint_graph=breakpoint_graph,
                      merge_edges=merge_edges)