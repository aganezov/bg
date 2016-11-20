# -*- coding: utf-8 -*-
import itertools
from copy import deepcopy

import networkx as nx
from networkx import MultiGraph

from bg.edge import BGEdge, BGEdge_JSON_SCHEMA_JSON_KEY
from bg.genome import BGGenome, BGGenome_JSON_SCHEMA_JSON_KEY
from bg.kbreak import KBreak
from bg.multicolor import Multicolor
from bg.utils import get_from_dict_with_path, merge_fragment_edge_data, recursive_dict_update
from bg.vertices import BGVertex_JSON_SCHEMA_JSON_KEY, BlockVertex, BGVertex, InfinityVertex, TaggedInfinityVertex, \
    TaggedBlockVertex, TaggedVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"


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
    *   :meth:`BreakpointGraph.edges_between_two_vertices`: returns a generator yielding :class:`bg.edge.BGEdge`  between two supplied vertices
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

    # class wide variables that are utilized in json deserialization process, when various types of vertices are obtained and processed
    # each deserialized class has a schema resolution dict specified below, and this dict can be updated on the fly, to specify more JSON schemas
    genomes_json_schemas = {"BGGenomeJSONSchema": BGGenome.BGGenomeJSONSchema}
    edges_json_schemas = {"BGEdgeJSONSchema": BGEdge.BGEdgeJSONSchema}
    vertices_json_schemas = {"BGVertexJSONSchema": BGVertex.BGVertexJSONSchema,
                             "BlockVertexJSONSchema": BlockVertex.BlockVertexJSONSchema,
                             "InfinityVertexJSONSchema": InfinityVertex.InfinityVertexJSONSchema,
                             "TaggedVertexJSONSchema": TaggedVertex.TaggedVertexJSONSchema,
                             "TaggedBlockVertexJSONSchema": TaggedBlockVertex.TaggedBlockVertexJSONSchema,
                             "TaggedInfinityVertexJSONSchema": TaggedInfinityVertex.TaggedInfinityVertexJSONSchema}

    def __init__(self, graph=None):
        """ Initialization of a :class:`BreakpointGraph` object.

        :param graph: is supplied, :class:`BreakpointGraph` is initialized with supplied or brand new (empty) instance of NetworkX MultiGraph.
        :type graph: instance of NetworkX MultiGraph is expected.
        """
        self.cache = {}
        self.cache_valid = {}
        if graph is None:
            self.bg = MultiGraph()
        else:
            self.bg = graph

    def __edges(self, nbunch=None, keys=False):
        """ Iterates over edges in current :class:`BreakpointGraph` instance.

        Returns a generator over the edges in current :class:`BreakpointGraph` instance producing instances of :class:`bg.edge.BGEdge` instances wrapping around information in underlying MultiGraph object.

        :param nbunch: a vertex to iterate over edges outgoing from, if not provided,iteration over all edges is performed.
        :type nbuch: any hashable python object
        :param keys: a flag to indicate if information about unique edge's ids has to be returned alongside with edge
        :type keys: ``Boolean``
        :return: generator over edges in current :class:`BreakpointGraph`
        :rtype: ``generator``
        """
        for v1, v2, key, data in self.bg.edges_iter(nbunch=nbunch, data=True, keys=True):
            bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=data["multicolor"], data=data["data"])
            if not keys:
                yield bgedge
            else:
                yield bgedge, key

    def edges(self, nbunch=None, keys=False):
        """ Iterates over edges in current :class:`BreakpointGraph` instance.

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__edges`.

        :param nbunch: a vertex to iterate over edges outgoing from, if not provided,iteration over all edges is performed.
        :type nbuch: any hashable python object
        :param keys: a flag to indicate if information about unique edge's ids has to be returned alongside with edge
        :type keys: ``Boolean``
        :return: generator over edges in current :class:`BreakpointGraph`
        :rtype: ``generator``
        """
        for entry in self.__edges(nbunch=nbunch, keys=keys):
            yield entry

    def nodes(self):
        """ Iterates over nodes in current :class:`BreakpointGraph` instance.

        :return:  generator over nodes (vertices) in current :class:`BreakpointGraph` instance.
        :rtype: ``generator``
        """
        for entry in self.bg.nodes_iter():
            yield entry

    def add_edge(self, vertex1, vertex2, multicolor, merge=True, data=None):
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
        self.__add_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor, data=data), merge=merge)

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
            self.bg[bgedge.vertex1][bgedge.vertex2][key]["data"] = {}
        else:
            self.bg.add_edge(u=bgedge.vertex1, v=bgedge.vertex2, attr_dict={"multicolor": deepcopy(bgedge.multicolor),
                                                                            "data": bgedge.data})
        self.cache_valid["overall_set_of_colors"] = False

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

        Returns a :class:`bg.vertex.BGVertex` or its subclass instance

        :param vertex_name: a vertex label it is identified by.
        :type vertex_name: any hashable python object. ``str`` expected.
        :return: vertex with supplied label if present in current :class:`BreakpointGraph`, ``None`` otherwise
        """
        vertex_class = BGVertex.get_vertex_class_from_vertex_name(vertex_name)
        data = vertex_name.split(BlockVertex.NAME_SEPARATOR)
        root_name, data = data[0], data[1:]
        if issubclass(vertex_class, TaggedVertex):
            tags = [entry.split(TaggedVertex.TAG_SEPARATOR) for entry in data]
            for tag_entry in tags:
                if len(tag_entry) == 1:
                    tag_entry.append(None)
                elif len(tag_entry) > 2:
                    tag_entry[1:] = [TaggedVertex.TAG_SEPARATOR.join(tag_entry[1:])]
            result = vertex_class(root_name)
            for tag, value in tags:
                if tag == InfinityVertex.NAME_SUFFIX and issubclass(vertex_class, InfinityVertex):
                    continue
                result.add_tag(tag, value)
        else:
            result = vertex_class(root_name)

        if result in self.bg:
            adjacencies = self.bg[result]
            for key, _ in adjacencies.items():
                for ref_key, values in self.bg[key].items():
                    if ref_key == result:
                        return ref_key
            return list(self.bg[result].keys())[0]
        return None

    def get_vertex_by_name(self, vertex_name):
        """ Obtains a vertex object by supplied label

        Proxies a call to :meth:`BreakpointGraph._BreakpointGraph__get_vertex_by_name`.

        :param vertex_name: a vertex label it is identified by.
        :type vertex_name: any hashable python object. ``str`` expected.
        :return: vertex with supplied label if present in current :class:`BreakpointGraph`, ``None`` otherwise
        :rtype: :class:`bg.vertices.BGVertex` or ``None``
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
            return BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=self.bg[vertex1][vertex2][key]["multicolor"],
                          data=self.bg[vertex1][vertex2][key]["data"])
        return None

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

    def __get_edges_by_vertex(self, vertex, keys=False):
        """ Iterates over edges that are incident to supplied vertex argument in current :class:`BreakpointGraph`

        Checks that the supplied vertex argument exists in underlying MultiGraph object as a vertex, then iterates over all edges that are incident to it. Wraps each yielded object into :class:`bg.edge.BGEdge` object.

        :param vertex: a vertex object in current :class:`BreakpointGraph` object
        :type vertex: any hashable object. :class:`bg.vertex.BGVertex` object is expected.
        :param keys: a flag to indicate if information about unique edge's ids has to be returned alongside with edge
        :type keys: ``Boolean``
        :return: generator over edges (tuples ``edge, edge_id`` if keys specified) in current :class:`BreakpointGraph` wrapped in :class:`bg.vertex.BGEVertex`
        :rtype: ``generator``
        """
        if vertex in self.bg:
            for vertex2, edges in self.bg[vertex].items():
                for key, data in self.bg[vertex][vertex2].items():
                    bg_edge = BGEdge(vertex1=vertex, vertex2=vertex2, multicolor=data["multicolor"], data=data["data"])
                    if keys:
                        yield bg_edge, key
                    else:
                        yield bg_edge

    def get_edges_by_vertex(self, vertex, keys=False):
        """ Iterates over edges that are incident to supplied vertex argument in current :class:`BreakpointGraph`

        Proxies a call to :meth:`Breakpoint._Breakpoint__get_edges_by_vertex` method.

        :param vertex: a vertex object in current :class:`BreakpointGraph` object
        :type vertex: any hashable object. :class:`bg.vertex.BGVertex` object is expected.
        :param keys: a flag to indicate if information about unique edge's ids has to be returned alongside with edge
        :type keys: ``Boolean``
        :return: generator over edges (tuples ``edge, edge_id`` if keys specified) in current :class:`BreakpointGraph` wrapped in :class:`bg.vertex.BGEVertex`
        :rtype: ``generator``
        """
        for entry in self.__get_edges_by_vertex(vertex=vertex, keys=keys):
            yield entry

    def __edges_between_two_vertices(self, vertex1, vertex2, keys=False):
        """ Iterates over edges between two supplied vertices in current :class:`BreakpointGraph`

        Checks that both supplied vertices are present in current breakpoint graph and then yield all edges that are located between two supplied vertices.
        If keys option is specified, then not just edges are yielded, but rather pairs (edge, edge_id) are yielded

        :param vertex1: a first vertex out of two, edges of interest are incident to
        :type vertex1: any hashable object, :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second vertex out of two, edges of interest are incident to
        :type vertex2: any hashable object, :class:`bg.vertex.BGVertex` is expected
        :param keys: a flag to indicate if information about unique edge's ids has to be returned alongside with edge
        :type keys: ``Boolean``
        :return: generator over edges (tuples ``edge, edge_id`` if keys specified) between two supplied vertices in current :class:`BreakpointGraph` wrapped in :class:`bg.vertex.BGVertex`
        :rtype: ``generator``
        """
        for vertex in vertex1, vertex2:
            if vertex not in self.bg:
                raise ValueError("Supplied vertex ({vertex_name}) is not present in current BreakpointGraph"
                                 "".format(vertex_name=str(vertex.name)))
        for bgedge, key in self.__get_edges_by_vertex(vertex=vertex1, keys=True):
            if bgedge.vertex2 == vertex2:
                if keys:
                    yield bgedge, key
                else:
                    yield bgedge

    def edges_between_two_vertices(self, vertex1, vertex2, keys=False):
        """ Iterates over edges between two supplied vertices in current :class:`BreakpointGraph`

        Proxies a call to :meth:`Breakpoint._Breakpoint__edges_between_two_vertices` method.

        :param vertex1: a first vertex out of two, edges of interest are incident to
        :type vertex1: any hashable object, :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second vertex out of two, edges of interest are incident to
        :type vertex2: any hashable object, :class:`bg.vertex.BGVertex` is expected
        :param keys: a flag to indicate if information about unique edge's ids has to be returned alongside with edge
        :type keys: ``Boolean``
        :return: generator over edges (tuples ``edge, edge_id`` if keys specified) between two supplied vertices in current :class:`BreakpointGraph` wrapped in :class:`bg.vertex.BGVertex`
        :rtype: ``generator``
        """
        for entry in self.__edges_between_two_vertices(vertex1=vertex1, vertex2=vertex2, keys=keys):
            yield entry

    def connected_components_subgraphs(self, copy=True):
        """ Iterates over connected components in current :class:`BreakpointGraph` object, and yields new instances of :class:`BreakpointGraph` with respective information deep-copied by default (week reference is possible of specified in method call).

        :param copy: a flag to signal if graph information has to be deep copied while producing new :class:`BreakpointGraph` instances, of just reference to respective data has to be made.
        :type copy: ``Boolean``
        :return: generator over connected components in current :class:`BreakpointGraph` wrapping respective connected components into new :class:`BreakpointGraph` objects.
        :rtype: ``generator``
        """
        for component in nx.connected_component_subgraphs(self.bg, copy=copy):
            yield BreakpointGraph(component)

    def __delete_bgedge(self, bgedge, key=None, keep_vertices=False):
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
        ############################################################################################################
        #
        # determines which edge to delete
        # candidate edges setup
        #
        ############################################################################################################

        if key is not None:
            ############################################################################################################
            #
            # is an edge specific key is provided, only edge with that key can undergo multicolor deletion
            # even if that edge is not the most suited to the edge to be deleted
            #
            ############################################################################################################
            self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"] -= bgedge.multicolor
            if len(self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"].multicolors) == 0:
                ############################################################################################################
                #
                # since edge deletion correspond to multicolor substitution one must make sure
                # that no edges with empty multicolor are left in the graph
                #
                ############################################################################################################
                self.bg.remove_edge(v=bgedge.vertex1, u=bgedge.vertex2, key=key)
                if keep_vertices:
                    self.bg.add_node(bgedge.vertex1)
                    self.bg.add_node(bgedge.vertex2)
        else:
            candidate_data, candidate_id, candidate_score = self.__determine_most_suitable_edge_for_deletion(bgedge)
            if candidate_data is not None:
                candidate_data["multicolor"] -= bgedge.multicolor
                if len(self.bg[bgedge.vertex1][bgedge.vertex2][candidate_id]["multicolor"].multicolors) == 0:
                    self.bg.remove_edge(v=bgedge.vertex1, u=bgedge.vertex2, key=candidate_id)
                    if keep_vertices:
                        self.bg.add_node(bgedge.vertex1)
                        self.bg.add_node(bgedge.vertex2)
        self.cache_valid["overall_set_of_colors"] = False

    def __determine_most_suitable_edge_for_deletion(self, bgedge):
        candidate_id = None
        candidate_score = -1
        candidate_data = None
        for v1, v2, key, data in self.bg.edges_iter(nbunch=bgedge.vertex1, data=True, keys=True):
            ############################################################################################################
            #
            # iterate over all edges and determine which edge has a multicolor most related to the provided for deletion edge
            #
            ############################################################################################################
            if v2 == bgedge.vertex2:
                score = Multicolor.similarity_score(bgedge.multicolor, data["multicolor"])
                if score > candidate_score:
                    candidate_id = key
                    candidate_data = data
                    candidate_score = score
        return candidate_data, candidate_id, candidate_score

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

    def __split_bgedge(self, bgedge, guidance=None, sorted_guidance=False,
                       account_for_colors_multiplicity_in_guidance=True, key=None):
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
            new_multicolors = Multicolor.split_colors(multicolor=self.bg[bgedge.vertex1][bgedge.vertex2][key]["multicolor"],
                                                      guidance=guidance, sorted_guidance=sorted_guidance,
                                                      account_for_color_multiplicity_in_guidance=account_for_colors_multiplicity_in_guidance)
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
                new_multicolors = Multicolor.split_colors(multicolor=candidate_data["multicolor"],
                                                          guidance=guidance, sorted_guidance=sorted_guidance,
                                                          account_for_color_multiplicity_in_guidance=account_for_colors_multiplicity_in_guidance)
                self.__delete_bgedge(bgedge=BGEdge(vertex1=bgedge.vertex1, vertex2=bgedge.vertex2,
                                                   multicolor=candidate_data["multicolor"]),
                                     key=candidate_id)
                for multicolor in new_multicolors:
                    self.__add_bgedge(BGEdge(vertex1=bgedge.vertex1, vertex2=bgedge.vertex2,
                                             multicolor=multicolor), merge=False)

    def split_edge(self, vertex1, vertex2, multicolor, guidance=None, sorted_guidance=False,
                   account_for_colors_multiplicity_in_guidance=True, key=None):
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
                            sorted_guidance=sorted_guidance,
                            account_for_colors_multiplicity_in_guidance=account_for_colors_multiplicity_in_guidance,
                            key=key)

    def split_bgedge(self, bgedge, guidance=None, sorted_guidance=False,
                     account_for_colors_multiplicity_in_guidance=True,
                     key=None):
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
        self.__split_bgedge(bgedge=bgedge, guidance=guidance, sorted_guidance=sorted_guidance,
                            account_for_colors_multiplicity_in_guidance=account_for_colors_multiplicity_in_guidance,
                            key=key)

    def __split_all_edges_between_two_vertices(self, vertex1, vertex2, guidance=None, sorted_guidance=False,
                                               account_for_colors_multiplicity_in_guidance=True):
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
            self.__split_bgedge(BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=None), guidance=guidance,
                                sorted_guidance=sorted_guidance,
                                account_for_colors_multiplicity_in_guidance=account_for_colors_multiplicity_in_guidance,
                                key=key)

    def split_all_edges_between_two_vertices(self, vertex1, vertex2, guidance=None, sorted_guidance=False,
                                             account_for_colors_multiplicity_in_guidance=True):
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
        self.__split_all_edges_between_two_vertices(vertex1=vertex1, vertex2=vertex2, guidance=guidance,
                                                    sorted_guidance=sorted_guidance,
                                                    account_for_colors_multiplicity_in_guidance=account_for_colors_multiplicity_in_guidance)

    def split_all_edges(self, guidance=None, sorted_guidance=False, account_for_colors_multiplicity_in_guidance=True):
        """ Splits all edge in current :class:`BreakpointGraph` instance with respect to the provided guidance.

        Iterate over all possible distinct pairs of vertices in current :class:`BreakpointGraph` instance and splits all edges between such pairs with respect to provided guidance.

        :param guidance: a guidance for underlying :class:`bg.multicolor.Multicolor` objects to be split
        :type guidance: iterable where each entry is iterable with colors entries
        :return: ``None``, performs inplace changes
        """
        vertex_pairs = [(edge.vertex1, edge.vertex2) for edge in self.edges()]
        for v1, v2 in vertex_pairs:
            self.__split_all_edges_between_two_vertices(vertex1=v1, vertex2=v2, guidance=guidance,
                                                        sorted_guidance=sorted_guidance,
                                                        account_for_colors_multiplicity_in_guidance=account_for_colors_multiplicity_in_guidance)

    def __delete_all_bgedges_between_two_vertices(self, vertex1, vertex2):
        """ Deletes all edges between two supplied vertices

        :param vertex1: a first out of two vertices edges between which are to be deleted
        :type vertex1: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :param vertex2: a second out of two vertices edges between which are to be deleted
        :type vertex2: any python hashable object. :class:`bg.vertex.BGVertex` is expected
        :return: ``None``, performs inplace changes
        """
        edges_to_be_deleted_with_keys = [(key, data) for v1, v2, key, data in self.bg.edges_iter(nbunch=vertex1, keys=True,
                                                                                                 data=True) if v2 == vertex2]
        for key, data in edges_to_be_deleted_with_keys:
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
        ############################################################################################################
        #
        # no actual merging is performed, but rather all edges between two vertices are deleted
        # and then added with a merge argument set to true
        #
        ############################################################################################################
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
        pairs_of_vetices = [(edge.vertex1, edge.vertex2) for edge in self.edges()]
        for v1, v2 in pairs_of_vetices:
            ############################################################################################################
            #
            # we iterate over all pairs of vertices in the given graph and merge edges between them
            #
            ############################################################################################################
            self.__merge_all_bgedges_between_two_vertices(vertex1=v1, vertex2=v2)

    @classmethod
    def merge(cls, breakpoint_graph1, breakpoint_graph2, merge_edges=False):
        """ Merges two given instances of :class`BreakpointGraph` into a new one, that gather all available information from both supplied objects.

        Depending of a ``merge_edges`` flag, while merging of two dat structures is occurring, edges between similar vertices can be merged during the creation of a result :class`BreakpointGraph` obejct.

        Accounts for subclassing.

        :param breakpoint_graph1: a first out of two :class`BreakpointGraph` instances to gather information from
        :type breakpoint_graph1: :class`BreakpointGraph`
        :param breakpoint_graph2: a second out of two :class`BreakpointGraph` instances to gather information from
        :type breakpoint_graph2: :class`BreakpointGraph`
        :param merge_edges: flag to indicate if edges in a new merged :class`BreakpointGraph` object has to be merged between same vertices, or if splitting from supplied graphs shall be preserved.
        :type merge_edges: ``Boolean``
        :return: a new breakpoint graph object that contains all information gathered from both supplied breakpoint graphs
        :rtype: :class`BreakpointGraph`
        """
        result = cls()
        for bgedge in breakpoint_graph1.edges():
            result.__add_bgedge(bgedge=bgedge, merge=merge_edges)
        for bgedge in breakpoint_graph2.edges():
            result.__add_bgedge(bgedge=bgedge, merge=merge_edges)
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

    def apply_kbreak(self, kbreak, merge=True):
        """ Check validity of supplied k-break and then applies it to current :class:`BreakpointGraph`

        Only :class:`bg.kbreak.KBreak` (or its heirs) instances are allowed as ``kbreak`` argument.
        KBreak must correspond to the valid kbreak and, since some changes to its internals might have been done since its creation, a validity check in terms of starting/resulting edges is performed.
        All vertices in supplied KBreak (except for paired infinity vertices) must be present in current :class:`BreakpointGraph`.
        For all supplied pairs of vertices (except for paired infinity vertices), there must be edges between such pairs of vertices, at least one of which must contain a multicolor matching a multicolor of supplied kbreak.

        Edges of specified in kbreak multicolor are deleted between supplied pairs of vertices in kbreak.start_edges (except for paired infinity vertices).
        New edges of specified in kbreak multicolor are added between all pairs of vertices in kbreak.result_edges (except for paired infinity vertices).
        If after the kbreak application there is an infinity vertex, that now has no edges incident to it, it is deleted form the current :class:`BreakpointGraph`.

        :param kbreak: a k-break to be applied to current :class:`BreakpointGraph`
        :type kbreak: `bg.kbreak.KBreak`
        :param merge: a flag to indicate on how edges, that will be created by a k-break, will be added to current :class:`BreakpointGraph`
        :type merge: ``Boolean``
        :return: nothing, performs inplace changes
        :rtype: ``None``
        :raises: ``ValueError``, ``TypeError``
        """
        ############################################################################################################
        #
        # k-break must ba valid to be applied
        #
        ############################################################################################################
        vertices = {}
        edge_data = {}
        if not isinstance(kbreak, KBreak):
            raise TypeError("Only KBreak and derivatives are allowed as kbreak argument")
        if not KBreak.valid_kbreak_matchings(kbreak.start_edges, kbreak.result_edges):
            raise ValueError("Supplied KBreak is not valid form perspective of starting/resulting sets of vertices")
        for vertex1, vertex2 in kbreak.start_edges:

            if vertex1.is_infinity_vertex and vertex2.is_infinity_vertex:
                ############################################################################################################
                #
                # when we encounter a fully infinity edge (both vertices are infinity vertices)
                # we shall not check if they are present in the current graph, because hat portion of a kbreak is artificial
                #
                ############################################################################################################
                continue
            if vertex1 not in self.bg or vertex2 not in self.bg:
                raise ValueError("Supplied KBreak targets vertices (`{v1}` and `{v2}`) at least one of which "
                                 "does not exist in current BreakpointGraph"
                                 "".format(v1=vertex1.name, v2=vertex2.name))
        for vertex1, vertex2 in kbreak.start_edges:
            if vertex1.is_infinity_vertex and vertex2.is_infinity_vertex:
                continue
            for bgedge in self.__edges_between_two_vertices(vertex1=vertex1, vertex2=vertex2):
                ############################################################################################################
                #
                # at least one edge between supplied pair of vertices must contain a multicolor that is specified for the kbreak
                #
                ############################################################################################################
                if kbreak.multicolor <= bgedge.multicolor:
                    break
            else:
                raise ValueError("Some targeted by kbreak edge with specified multicolor does not exists")
        for vertex1, vertex2 in kbreak.start_edges:
            if vertex1.is_infinity_vertex and vertex2.is_infinity_vertex:
                continue
            v1 = self.__get_vertex_by_name(vertex_name=vertex1.name)
            vertices[v1] = v1
            v2 = self.__get_vertex_by_name(vertex_name=vertex2.name)
            vertices[v2] = v2
            bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=kbreak.multicolor)
            candidate_data, candidate_id, candidate_score = self.__determine_most_suitable_edge_for_deletion(bgedge=bgedge)
            data = candidate_data["data"]
            edge_data[v1] = data
            edge_data[v2] = data
            self.__delete_bgedge(bgedge=bgedge, keep_vertices=True)
        for vertex_set in kbreak.start_edges:
            for vertex in vertex_set:
                if vertex.is_infinity_vertex and vertex in self.bg:
                    ############################################################################################################
                    #
                    # after the first portion of a kbreak is performed one must make sure we don't leave any infinity vertices
                    # that have edges going to them, as infinity vertex is a special artificial vertex
                    #  and it has meaning only if there are edges going to / from it
                    #
                    ############################################################################################################
                    if len(list(self.get_edges_by_vertex(vertex=vertex))) == 0:
                        self.bg.remove_node(vertex)
        for vertex1, vertex2 in kbreak.result_edges:
            if vertex1.is_infinity_vertex and vertex2.is_infinity_vertex:
                ############################################################################################################
                #
                # if we encounter a pair of infinity vertices in result edges set, we shall not add them
                # as at least a part of kbreak corresponded to fusion
                # and those infinity edges on their own won't have any meaning
                #
                ############################################################################################################
                continue
            origin = kbreak.data.get("origin", None)
            v1 = vertices.get(vertex1, vertex1)
            v2 = vertices.get(vertex2, vertex2)
            bg_edge = BGEdge(vertex1=v1, vertex2=v2, multicolor=kbreak.multicolor)
            if "origin" in bg_edge.data:
                bg_edge.data["origin"] = origin
            if kbreak.is_a_fusion:
                edge1_data = edge_data[v1]
                edge2_data = edge_data[v2]
                merged_edge_fragment_data = merge_fragment_edge_data(edge1_data["fragment"], edge2_data["fragment"])
                result_edge_data = {}
                recursive_dict_update(result_edge_data, edge1_data)
                recursive_dict_update(result_edge_data, edge2_data)
                recursive_dict_update(result_edge_data, {"fragment": merged_edge_fragment_data})
                recursive_dict_update(bg_edge.data, result_edge_data)
            self.__add_bgedge(bg_edge, merge=merge)

    def to_json(self, schema_info=True):
        """ JSON serialization method that account for all information-wise important part of breakpoint graph
        """
        genomes = set()
        result = {}
        result["edges"] = []
        for bgedge in self.edges():
            genomes |= bgedge.multicolor.colors
            result["edges"].append(bgedge.to_json(schema_info=schema_info))
        result["vertices"] = [bgvertex.to_json(schema_info=schema_info) for bgvertex in self.nodes()]
        result["genomes"] = [bggenome.to_json(schema_info=schema_info) for bggenome in genomes]
        return result

    @classmethod
    def from_json(cls, data, genomes_data=None, genomes_deserialization_required=True, merge=False):
        """ A JSON deserialization operation, that recovers a breakpoint graph from its JSON representation

          as information about genomes, that are encoded in breakpoint graph might be available somewhere else, but not the
          json object, there is an option to provide it and omit encoding information about genomes.
        """
        result = cls()
        merge = merge
        vertices_dict = {}
        genomes_dict = genomes_data if genomes_data is not None and not genomes_deserialization_required else None
        if genomes_dict is None:
            ############################################################################################################
            #
            # if we need to recover genomes information from breakpoint graph json object
            # we are happy to do that
            #
            ############################################################################################################
            genomes_dict = {}
            try:
                source = genomes_data if genomes_data is not None and genomes_deserialization_required else data["genomes"]
            except KeyError as exc:
                raise ValueError("Error during breakpoint graph deserialization. No \"genomes\" information found")
            for g_dict in source:
                ############################################################################################################
                #
                # if explicitly specified in genome json object, it can be decoded using provided schema name,
                # of course a decoding breakpoint graph object shall be aware of such scheme
                # (it has to be specified in the `genomes_json_schemas` class wide dict)
                #
                ############################################################################################################
                schema_name = g_dict.get(BGGenome_JSON_SCHEMA_JSON_KEY, None)
                schema_class = None if schema_name is None else cls.genomes_json_schemas.get(schema_name, None)
                genomes_dict[g_dict["g_id"]] = BGGenome.from_json(data=g_dict, json_schema_class=schema_class)
        if "vertices" not in data:
            ############################################################################################################
            #
            # breakpoint graph can not be decoded without having information about vertices explicitly
            # as vertices are referenced in edges object, rather than explicitly provided
            #
            ############################################################################################################
            raise ValueError("Error during breakpoint graph deserialization. \"vertices\" key is not present in json object")
        for vertex_dict in data["vertices"]:
            ############################################################################################################
            #
            # if explicitly specified in vertex json object, it can be decoded using provided schema name,
            # of course a decoding breakpoint graph object shall be aware of such scheme
            # (it has to be specified in the `vertices_json_schemas` class wide dict)
            #
            ############################################################################################################
            schema_name = vertex_dict.get(BGVertex_JSON_SCHEMA_JSON_KEY, None)
            schema_class = None if schema_name is None else cls.vertices_json_schemas.get(schema_name, None)
            try:
                ############################################################################################################
                #
                # we try to recover a specific vertex class based on its name.
                # it does not overwrite the schema based behaviour
                # but provides a correct default schema for a specific vertex type
                #
                ############################################################################################################
                vertex_class = BGVertex.get_vertex_class_from_vertex_name(vertex_dict["name"])
            except KeyError:
                vertex_class = BGVertex
            vertices_dict[vertex_dict["v_id"]] = vertex_class.from_json(data=vertex_dict, json_schema_class=schema_class)
        for edge_dict in data["edges"]:
            ############################################################################################################
            #
            # if explicitly specified in edge json object, it can be decoded using provided schema name,
            # of course a decoding breakpoint graph object shall be aware of such scheme
            # (it has to be specified in the `edges_json_schemas` class wide dict)
            #
            ############################################################################################################
            schema_name = edge_dict.get(BGEdge_JSON_SCHEMA_JSON_KEY, None)
            schema = None if schema_name is None else cls.edges_json_schemas.get(schema_name, None)
            edge = BGEdge.from_json(data=edge_dict, json_schema_class=schema)
            try:
                edge.vertex1 = vertices_dict[edge.vertex1]
                edge.vertex2 = vertices_dict[edge.vertex2]
            except KeyError:
                ############################################################################################################
                #
                # as edge references a pair of vertices, we must be sure respective vertices were decoded
                #
                ############################################################################################################
                raise ValueError("Error during breakpoint graph deserialization. Deserialized edge references non-present vertex")
            if len(edge.multicolor) == 0:
                ############################################################################################################
                #
                # edges with empty multicolor are not permitted in breakpoint graphs
                #
                ############################################################################################################
                raise ValueError("Error during breakpoint graph deserialization. Empty multicolor for deserialized edge")
            try:
                edge.multicolor = Multicolor(*[genomes_dict[g_id] for g_id in edge.multicolor])
            except KeyError:
                raise ValueError("Error during breakpoint graph deserialization. Deserialized edge reference non-present "
                                 "genome in its multicolor")
            result.__add_bgedge(edge, merge=merge)
        return result

    def get_overall_set_of_colors(self):
        if "overall_set_of_colors" not in self.cache_valid or not self.cache_valid["overall_set_of_colors"]:
            self.cache["overall_set_of_colors"] = {color for bg_edge in self.edges() for color in bg_edge.multicolor.colors}
            self.cache_valid["overall_set_of_colors"] = True
        return self.cache["overall_set_of_colors"]

    def get_genome_graph(self, color):
        result = BreakpointGraph()
        mc = Multicolor(color)
        for edge in self.edges():
            if mc <= edge.multicolor:
                result.__add_bgedge(bgedge=BGEdge(vertex1=edge.vertex1, vertex2=edge.vertex2,
                                                  multicolor=mc, data=edge.data))
        return result

    def get_blocks_order(self):
        genome = self.get_overall_set_of_colors().pop()
        result = {genome: []}
        visited_vertices = set()
        for vertex in self.nodes():
            if vertex in visited_vertices:
                continue
            visited_vertices.add(vertex)
            chr_type_f, fragment_part_forward = self._traverse_blocks_forward_from_vertex(vertex=vertex, visited_vertices=visited_vertices)
            chr_type_r, fragment_part_reverse = self._traverse_blocks_reverse_from_vertex(vertex=vertex, visited_vertices=visited_vertices)
            if chr_type_f != chr_type_r:
                raise Exception("During the gene order sequence traversal we got a conflicted situation. "
                                "Most probably case for this to happen is to have a genome with non-unique gene content")
            if chr_type_f == "$":
                fragment = fragment_part_reverse + fragment_part_forward
            else:
                fragment = fragment_part_forward if len(fragment_part_forward) > len(fragment_part_reverse) else fragment_part_reverse
            result[genome].append((chr_type_f, fragment))
        return result

    def _traverse_blocks_from_vertex(self, vertex, visited_vertices, direction):
        result = []
        current_vertex = vertex
        visited_vertices.add(current_vertex)
        if current_vertex.is_irregular_vertex:
            edge = list(self.get_edges_by_vertex(vertex=current_vertex))[0]
            current_vertex = edge.vertex1 if edge.vertex1 != current_vertex else edge.vertex2
            visited_vertices.add(current_vertex)
        if current_vertex.is_tail_vertex and direction == "forward" or current_vertex.is_head_vertex and direction == "reverse":
            result.append(("+", current_vertex.block_name))
            current_vertex = current_vertex.mate_vertex
            visited_vertices.add(current_vertex)
        edge = list(self.get_edges_by_vertex(vertex=current_vertex))[0]
        current_vertex = edge.vertex1 if edge.vertex1 != current_vertex else edge.vertex2
        while current_vertex not in visited_vertices and current_vertex.is_regular_vertex:
            visited_vertices.add(current_vertex)
            if direction == "forward":
                sign = "+" if current_vertex.is_tail_vertex else "-"
            elif direction == "reverse":
                sign = "-" if current_vertex.is_tail_vertex else "+"
            else:
                sign = "*"
            result.append((sign, current_vertex.block_name))
            current_vertex = current_vertex.mate_vertex
            visited_vertices.add(current_vertex)
            edge = list(self.get_edges_by_vertex(vertex=current_vertex))[0]
            current_vertex = edge.vertex1 if edge.vertex1 != current_vertex else edge.vertex2
        visited_vertices.add(current_vertex)
        if current_vertex.is_irregular_vertex:
            chr_type = "$"
        else:
            chr_type = "@"
        if direction == "reverse":
            result = result[::-1]
        return chr_type, result

    def _traverse_blocks_forward_from_vertex(self, vertex, visited_vertices):
        return self._traverse_blocks_from_vertex(vertex=vertex, visited_vertices=visited_vertices, direction="forward")

    def _traverse_blocks_reverse_from_vertex(self, vertex, visited_vertices):
        return self._traverse_blocks_from_vertex(vertex=vertex, visited_vertices=visited_vertices, direction="reverse")

    def _traverse_fragments_forward_from_vertex(self, vertex, visited_vertices):
        return self._traverse_fragments_from_vertex(vertex=vertex, visited_vertices=visited_vertices, direction="forward")

    def _traverse_fragments_reverse_from_vertex(self, vertex, visited_vertices):
        return self._traverse_fragments_from_vertex(vertex=vertex, visited_vertices=visited_vertices, direction="reverse")

    def has_edge(self, vertex1, vertex2):
        return self.bg.has_edge(u=vertex1, v=vertex2)

    def get_condensed_edge(self, vertex1, vertex2):
        if not self.has_edge(vertex1=vertex1, vertex2=vertex2):
            return None
        result = BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=Multicolor())
        for edge in self.__edges_between_two_vertices(vertex1=vertex1, vertex2=vertex2):
            result.multicolor += edge.multicolor
        return result

    def get_fragments_orders(self):
        genome = self.get_overall_set_of_colors().pop()
        result = {genome: []}
        visited_vertices = set()
        ivs = (v for v in self.nodes() if v.is_irregular_vertex)
        rvs = (v for v in self.nodes() if v.is_regular_vertex)
        for vertex in itertools.chain(ivs, rvs):
            if vertex in visited_vertices:
                continue
            chr_type_f, fragments_order_part_forward = self._traverse_fragments_forward_from_vertex(vertex=vertex,
                                                                                                    visited_vertices=visited_vertices)
            chr_type_r, fragments_order_part_reverse = self._traverse_fragments_reverse_from_vertex(vertex=vertex,
                                                                                                    visited_vertices=visited_vertices)
            if chr_type_f != chr_type_r:
                raise Exception("During the fragment order sequence traversal we got a conflicted situation. "
                                "Most probably case for this to happen is to have a genome with non-unique gene content")
            if chr_type_f == "$":
                if len(fragments_order_part_forward) == 0:
                    fragment = fragments_order_part_reverse
                elif len(fragments_order_part_reverse) == 0:
                    fragment = fragments_order_part_forward
                else:
                    coincide = fragments_order_part_reverse[-1][0] == fragments_order_part_forward[0][0]
                    coincide &= fragments_order_part_reverse[-1][1] == fragments_order_part_forward[0][1]
                    if coincide:
                        fragment = fragments_order_part_reverse[:-1] + fragments_order_part_forward
                    else:
                        fragment = fragments_order_part_reverse + fragments_order_part_forward
            else:
                fragment = fragments_order_part_forward if len(fragments_order_part_forward) > len(
                        fragments_order_part_reverse) else fragments_order_part_reverse
                if len(fragment) > 1 and fragment[-1][0] == fragment[0][0] and fragment[-1][1] == fragment[0][1]:
                    fragment = fragment[:-1]
            result[genome].append((chr_type_f, fragment))
        return result

    def _traverse_fragments_from_vertex(self, vertex, visited_vertices, direction):
        result = []
        current_vertex = vertex
        current_fragment_name = None
        current_fragment_orientation = None
        if current_vertex.is_tail_vertex and direction == "forward" or current_vertex.is_head_vertex and direction == "reverse":
            current_vertex = current_vertex.mate_vertex
        elif not (current_vertex.is_irregular_vertex and current_vertex in visited_vertices):
            visited_vertices.add(current_vertex)
            edge = list(self.get_edges_by_vertex(vertex=current_vertex))[0]
            fragment_names = get_from_dict_with_path(source_dict=edge.data, key="name", path=["fragment"])
            if not isinstance(fragment_names, list):
                fragment_names = [fragment_names]
            fragment_orientations = self._get_fragment_to_edge_orientation(current_vertex=current_vertex, edge=edge)
            fragment_orientations = self.update_orientation_with_direction(orientation=fragment_orientations,
                                                                           direction=direction)
            for name, orientation in zip(fragment_names, fragment_orientations):
                new_encounter = current_fragment_name != name or current_fragment_orientation != name
                if name not in [None, ""] and orientation not in [None, ""] and new_encounter:
                    current_fragment_name = name
                    current_fragment_orientation = orientation
                    result.append((current_fragment_orientation, current_fragment_name))
            current_vertex = edge.vertex1 if edge.vertex1 != current_vertex else edge.vertex2
            visited_vertices.add(current_vertex)
            if not current_vertex.is_irregular_vertex:
                current_vertex = current_vertex.mate_vertex
        while current_vertex not in visited_vertices and not current_vertex.is_irregular_vertex:
            visited_vertices.add(current_vertex)
            edge = list(self.get_edges_by_vertex(vertex=current_vertex))[0]
            fragment_names = get_from_dict_with_path(source_dict=edge.data, key="name", path=["fragment"])
            if not isinstance(fragment_names, list):
                fragment_names = [fragment_names]
            fragment_orientations = self._get_fragment_to_edge_orientation(current_vertex=current_vertex, edge=edge)
            fragment_orientations = self.update_orientation_with_direction(orientation=fragment_orientations,
                                                                           direction=direction)
            if current_fragment_name == fragment_names[-1]:
                fragment_names = fragment_names[::-1]
                fragment_orientations = fragment_orientations[::-1]
            for name, orientation in zip(fragment_names, fragment_orientations):
                initial_state = current_fragment_name is None or current_fragment_orientation is None
                new_encounter = current_fragment_name != name or current_fragment_orientation != orientation
                new_encounter &= name not in [None, ""] and orientation not in [None, ""]
                if initial_state or new_encounter:
                    current_fragment_name = name
                    current_fragment_orientation = orientation
                    if current_fragment_name not in [None, ""] and current_fragment_orientation not in [None, ""]:
                        result.append((current_fragment_orientation, current_fragment_name))
            current_vertex = edge.vertex1 if edge.vertex1 != current_vertex else edge.vertex2
            if current_vertex.is_irregular_vertex:
                break
            visited_vertices.add(current_vertex)
            current_vertex = current_vertex.mate_vertex

        visited_vertices.add(current_vertex)
        if current_vertex.is_irregular_vertex:
            chr_type = "$"
        else:
            chr_type = "@"
        if direction == "reverse":
            result = result[::-1]
        return chr_type, result

    @staticmethod
    def _get_fragment_to_edge_orientation(current_vertex, edge):
        v1, v2 = (edge.vertex1, edge.vertex2) if edge.vertex1 == current_vertex else (edge.vertex2, edge.vertex1)
        forward_orientation = get_from_dict_with_path(source_dict=edge.data, key="forward_orientation", path=["fragment"])
        if isinstance(forward_orientation, list):
            return ["+" if BreakpointGraph._forward_orientation(v1, v2, orientation) else "-" for orientation in forward_orientation]
        else:
            return ["+" if BreakpointGraph._forward_orientation(v1, v2, forward_orientation) else "-"]

    @staticmethod
    def _forward_orientation(v1, v2, forward_orientation):
        if forward_orientation is None:
            return True
        left_v = v1 not in forward_orientation or forward_orientation[0] == v1
        right_v = v2 not in forward_orientation or forward_orientation[1] == v2
        return left_v and right_v

    @staticmethod
    def update_orientation_with_direction(orientation, direction):
        result = []
        for entry in orientation:
            if direction == "forward":
                result.append(entry)
            else:
                result.append("-" if entry == "+" else "+")
        return result


class BGConnectedComponentFilter(object):
    def __init__(self):
        self.name = None

    def accept_connected_component(self, cc, breakpoint_graph=None):
        return True


class CompleteMultiEdgeConnectedComponentFilter(BGConnectedComponentFilter):
    def __init__(self):
        super(CompleteMultiEdgeConnectedComponentFilter, self).__init__()
        self.name = "Complete ME filter"

    def accept_connected_component(self, cc, breakpoint_graph=None):
        if len(list(cc.nodes())) != 2:
            return True
        genomes_cnt = len(breakpoint_graph.get_overall_set_of_colors())
        edges_genomes_cnt = len({color for edge in cc.edges() for color in edge.multicolor.colors})
        return genomes_cnt != edges_genomes_cnt


class TwoNodeConnectedComponentFilter(BGConnectedComponentFilter):
    def __init__(self):
        super(TwoNodeConnectedComponentFilter, self).__init__()
        self.name = "Two node filter"

    def accept_connected_component(self, cc, breakpoint_graph=None):
        return len(list(cc.nodes())) != 2
