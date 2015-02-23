# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class BGEdge(object):
    """ A wrapper class for edges in :class:`bg.breakpoint_graph.BreakpointGraph`

    Is not stored on its own in the :class:`bg.breakpoint_graph.BreakpointGraph`, but is rather can be supplied to work with and is returned if retrieval is performed.
    BGEdge represents an undirected edge, thus distinction between :attr:`BGEdge.vertex1` and :attr:`BGEdge.vertex2` attributes is just from identities perspective, not from the order perspective.

    This class supports th following attributes, that cary information about multi-color for this edge, as well as vertices, its is attached to:

    *   :attr:`BGEdge.vertex1`: a first vertex to be utilized in :class:`bg.breakpoint_graph.BreakpointGraph`. Expected to store :class:`bg.vertex.BGVertex`.
    *   :attr:`BGEdge.vertex2`: a second vertex to be utilized in :class:`bg.breakpoint_graph.BreakpointGraph`. Expected to store :class:`bg.vertex.BGVertex`.

    Main operations:

    *   ``==``
    *   :meth:`BGEdge.merge`: produces a new BGEdge with multi-color information being merged from them
    """
    def __init__(self, vertex1, vertex2, multicolor):
        """ Initialization of :class:`BGEdge` object.

        :param vertex1: vertex the edges is outgoing from
        :type vertex1: any hashable python object. :class:`bg.vertex.BGVertex` is expected.
        :param vertex2: vertex the edges is ingoing to
        :type vertex2: any hashable python object. :class:`bg.vertex.BGVertex` is expected.
        :param multicolor: multicolor that this single edge shall posses
        :type multicolor: :class:`bg.multicolor.Multicolor`
        :return: ``None``, performs initialization of respective instance of :class:`BGEdge`
        """

        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.multicolor = multicolor

    @staticmethod
    def merge(edge1, edge2):
        """ Merges multi-color information from two supplied :class:`BGEdge` instances into a new :class:`BGEdge`

        Since :class:`BGEdge` represents an undirected edge, created edge's vertices are assign accordint to the order in first supplied edge.

        :param edge1: first out of two edge information from which is to be merged into a new one
        :type edge1:
        :param edge2: second out of two edge information from which is to be merged into a new one
        :type edge2:
        :return: a new undirected with multi-color information merged from two supplied :class:`BGEdge` objects
        :rtype: :class:`BGEdge`
        :raises: ``ValueError``
        """
        if edge1.vertex1 != edge2.vertex1 and edge1.vertex1 != edge2.vertex2:
            raise ValueError("Edges to be merged do not connect same vertices")
        forward = edge1.vertex1 == edge2.vertex1
        if forward and edge1.vertex2 != edge2.vertex2:
            raise ValueError("Edges to be merged do not connect same vertices")
        elif not forward and edge1.vertex2 != edge2.vertex1:
            raise ValueError("Edges to be merged do not connect same vertices")
        return BGEdge(vertex1=edge1.vertex1, vertex2=edge1.vertex2, multicolor=edge1.multicolor + edge2.multicolor)

    def __eq__(self, other):
        """ Implementation of ``==`` operation for :class:`BGEdge`

        Checks if current :class:`BGEdge` instance comply in terms of vertices set with the supplied :class:`BGEdge`, and then checks the equality of :attr:`BGEdge.multicolor` attributes in respective objects.
         :class:`BGEdge` does not equal to non-:class:`BGEdge` objects

        :param other: object to compare current :class:`BGEdge` to
        :type other: any python object
        :return: flag of equality if current :class:`BGEdge` object equals to the supplied one
        :rtype: ``Boolean``
        """
        if not isinstance(other, BGEdge):
            return False
        if self.vertex1 != other.vertex1 and self.vertex1 != other.vertex2:
            return False
        multicolor_equality = self.multicolor == other.multicolor
        if self.vertex1 == other.vertex1:
            return self.vertex2 == other.vertex2 and multicolor_equality
        else:
            return self.vertex2 == other.vertex1 and multicolor_equality