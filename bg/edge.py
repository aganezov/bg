# -*- coding: utf-8 -*-
from marshmallow import Schema, fields
from bg.vertex import INFINITY_VERTEX_IDENTIFIER

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

BGEdge_JSON_SCHEMA_JSON_KEY = "_py__bg_edge_json_schema"


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

    class BGEdgeJSONSchema(Schema):
        _py__bg_edge_json_schema = fields.String(attribute="json_schema_name")
        vertex1_id = fields.Int(attribute="vertex1_json_id", required=True)
        vertex2_id = fields.Int(attribute="vertex2_json_id", required=True)
        multicolor = fields.List(fields.Int, attribute="colors_json_ids", allow_none=False, required=True)

        def make_object(self, data):
            if "vertex1_json_id" not in data:
                raise ValueError("Error during edge serialization. \"vertex1_id\" key is not present in json object")
            vertex1 = data["vertex1_json_id"]
            if "vertex2_json_id" not in data:
                raise ValueError("Error during edge serialization. \"vertex2_id\" key is not present in json object")
            vertex2 = data["vertex2_json_id"]
            if "colors_json_ids" not in data:
                raise ValueError("Error during edge serialization. \"multicolor\" key is not present in json object")
            multicolor = data["colors_json_ids"]
            return BGEdge(vertex1=vertex1, vertex2=vertex2, multicolor=multicolor)

    json_schema = BGEdgeJSONSchema()

    def __init__(self, vertex1, vertex2, multicolor):
        """ Initialization of :class:`BGEdge` object.

        :param vertex1: vertex the edges is outgoing from
        :type vertex1: any hashable python object. :class:`bg.vertex.BGVertex` is expected.
        :param vertex2: vertex the edges is ingoing to
        :type vertex2: any hashable python object. :class:`bg.vertex.BGVertex` is expected.
        :param multicolor: multicolor that this single edge shall posses
        :type multicolor: :class:`bg.multicolor.Multicolor`
        :return: a new instance of :class:`BGEdge`
        :rtype: :class:`BGEdge`
        """

        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.multicolor = multicolor

    @classmethod
    def merge(cls, edge1, edge2):
        """ Merges multi-color information from two supplied :class:`BGEdge` instances into a new :class:`BGEdge`

        Since :class:`BGEdge` represents an undirected edge, created edge's vertices are assign accordint to the order in first supplied edge.

        Accounts for subclassing.

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
        return cls(vertex1=edge1.vertex1, vertex2=edge1.vertex2, multicolor=edge1.multicolor + edge2.multicolor)

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

    @property
    def is_infinity_edge(self):
        return INFINITY_VERTEX_IDENTIFIER in self.vertex1.name or INFINITY_VERTEX_IDENTIFIER in self.vertex2.name

    @property
    def json_schema_name(self):
        return self.json_schema.__class__.__name__

    @staticmethod
    def __vertex_json_id(vertex):
        if hasattr(vertex, "json_id"):
            return vertex.json_id
        return hash(vertex)

    @property
    def vertex1_json_id(self):
        return self.__vertex_json_id(self.vertex1)

    @property
    def vertex2_json_id(self):
        return self.__vertex_json_id(self.vertex2)

    @property
    def colors_json_ids(self):
        return [color.json_id if hasattr(color, "json_id") else hash(color) for color in self.multicolor.multicolors.elements()]

    def to_json(self, schema_info=True):
        old_exclude_fields = self.json_schema.exclude
        new_exclude_fields = list(old_exclude_fields)
        if not schema_info:
            new_exclude_fields.append(BGEdge_JSON_SCHEMA_JSON_KEY)
        self.json_schema.exclude = new_exclude_fields
        result = self.json_schema.dump(self).data
        self.json_schema.exclude = old_exclude_fields
        return result

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return schema.load(data).data
