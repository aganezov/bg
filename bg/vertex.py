# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

INFINITY_VERTEX_IDENTIFIER = "__infinity"


class BGVertex(object):
    """ A wrapper class used to store information about vertex in the :class:`bg.breakpoint_graph.BreakpointGraph` data structure

    This class supports the following attributes, that carry information each BGVertex instances:

    *    :attr:`BGVertex.name`: main field used for vertex label and is used for comparison
    *    :attr:`BGVertex.info`: key:value type storage that might be sued to store additional information about respective vertex
    """
    def __init__(self, name, info=None):
        """ Initialization of BGVertex instance

        :param name: unique label for respective vertex to be identified in :class:`bg.breakpoint_graph.BreakpointGraph`
        :type name: any hashable object
        :param info: additional data about the vertex
        :type info: assumed to be {key:value} typed object
        :return: a new instance of :class:`BGVertex`
        :rtype: :class:`BGVertex`
        """
        self.name = name
        if info is None:
            info = {}
        self.info = info

    def __hash__(self):
        """ Specific implementation of self-hashable algorithm, that proxies the hash call to instance :attr:`BGVertex.name` attribute

        :return: hash of :attr:`BGVertex.name` value
        """
        return hash(self.name)

    def __eq__(self, other):
        """ Provides support for == comparison with other :class:`BGVertex` instance

        In case supplied object is not of :class:`BGVertex` type, returns `False`,
        otherwise comparison result between respective :attr:`BGVertex.name` attributes is returned

        :param other: other python object to compare current instance of :class:`BGVertex` to
        :type other: any python object
        :return: result of comparison between current :class:`BGVertex` and supplied python object
        :rtype: ``Boolean``
        """
        if not isinstance(other, BGVertex):
            return False
        return self.name == other.name

    @staticmethod
    def construct_infinity_vertex_companion(vertex):
        """ Creates a new vertex, that would correspond to the infinity vertex for supplied one

        In :class:`bg.breakpoint_graph.BreakpointGraph` is a vertex correspond to the blocks end, that is the outermost on some fragment, in breakpoint graph this fragment extremity is denoted by the the infinity edge to the infinity vertex, that accompanies respected gene extremity vertex.

        :param vertex: a vertex instance, to which a companion infinity vertex has to bre created
        :type vertex: ``str`` or :class:`BGVertex`
        :return: an infinity vertex instance that accompanies supplied vertex in :class:`bg.breakpoint_graph.BreakpointGraph`
        :rtype: ``str`` or :class:`BGVertex`
        """
        if isinstance(vertex, BGVertex):
            return BGVertex(vertex.name + INFINITY_VERTEX_IDENTIFIER)
        return vertex + INFINITY_VERTEX_IDENTIFIER

    @staticmethod
    def is_infinity_vertex(vertex):
        """ Check is supplied vertex is an "infinity" vertex in :class:`bg.breakpoint_graph.BreakpointGraph`

        :param vertex: a vertex to check "infinity" properties in
        :type vertex: any with ``name`` attribute, :class:`BGVertex` is expected
        :return: a flag indicating if supplied vertex is an "infinity" vertex
        :rtype: ``Boolean``
        """
        return INFINITY_VERTEX_IDENTIFIER in vertex.name
