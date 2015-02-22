# -*- coding: utf-8 -*-
__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


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
        :return: ``None``, performs initialization of respective instance of :class:`BGVertex`
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