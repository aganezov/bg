# -*- coding: utf-8 -*-
from marshmallow import Schema, fields

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

INFINITY_VERTEX_IDENTIFIER = "__infinity"
BGVertex_JSON_SCHEMA_JSON_KEY = "_py__bg_vertex_json_schema"


class OldBGVertex(object):
    """ A wrapper class used to store information about vertex in the :class:`bg.breakpoint_graph.BreakpointGraph` data structure

    This class supports the following attributes, that carry information each BGVertex instances:

    *    :attr:`BGVertex.name`: main field used for vertex label and is used for comparison
    *    :attr:`BGVertex.info`: key:value type storage that might be sued to store additional information about respective vertex
    """
    class BGVertexJSONSchema(Schema):
        name = fields.String(required=True, attribute="name")
        v_id = fields.Int(required=True, attribute="json_id")
        _py__bg_vertex_json_schema = fields.String(attribute="json_schema_name")

        def make_object(self, data):
            try:
                return OldBGVertex(name=data["name"])
            except KeyError as err:
                raise err

    json_schema = BGVertexJSONSchema()

    def __init__(self, name, info=None):
        """ Initialization of BGVertex instance

        :param name: unique label for respective vertex to be identified in :class:`bg.breakpoint_graph.BreakpointGraph`
        :type name: any hashable object
        :param info: additional data about the vertex
        :type info: assumed to be {key:value} typed object
        :return: a new instance of :class:`BGVertex`
        :rtype: :class:`OldBGVertex`
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
        if not isinstance(other, OldBGVertex):
            return False
        return self.name == other.name

    @classmethod
    def construct_infinity_vertex_companion(cls, vertex):
        """ Creates a new vertex, that would correspond to the infinity vertex for supplied one

        In :class:`bg.breakpoint_graph.BreakpointGraph` is a vertex correspond to the blocks end, that is the outermost on some fragment, in breakpoint graph this fragment extremity is denoted by the the infinity edge to the infinity vertex, that accompanies respected gene extremity vertex.

        Accounts for subclassing.

        :param vertex: a vertex instance, to which a companion infinity vertex has to bre created
        :type vertex: ``str`` or :class:`OldBGVertex`
        :return: an infinity vertex instance that accompanies supplied vertex in :class:`bg.breakpoint_graph.BreakpointGraph`
        :rtype: ``str`` or :class:`OldBGVertex`
        """
        if isinstance(vertex, cls):
            return cls(vertex.name + INFINITY_VERTEX_IDENTIFIER)
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

    @property
    def json_id(self):
        return hash(self)

    @property
    def json_schema_name(self):
        return self.json_schema.__class__.__name__

    def to_json(self, schema_info=True):
        old_exclude_fields = self.json_schema.exclude
        new_exclude_fields = list(old_exclude_fields)
        if not schema_info:
            new_exclude_fields.append(BGVertex_JSON_SCHEMA_JSON_KEY)
        self.json_schema.exclude = new_exclude_fields
        result = self.json_schema.dump(self).data
        self.json_schema.exclude = old_exclude_fields
        return result

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return schema.load(data).data


class BGVertex(object):

    class BGVertexJSONSchema(Schema):
        name = fields.String(required=True, attribute="name")
        v_id = fields.Int(required=True, attribute="json_id")
        _py__bg_vertex_json_schema = fields.String(attribute="json_schema_name")

    json_schema = BGVertexJSONSchema()

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __getattr__(self, item):
        if item.startswith("is_") and item.endswith("_vertex"):
            return False
        return super().__getattribute__(item)

    @property
    def json_id(self):
        return hash(self)

    @property
    def json_schema_name(self):
        return self.json_schema.__class__.__name__

    def to_json(self, schema_info=True):
        old_exclude_fields = self.json_schema.exclude
        new_exclude_fields = list(old_exclude_fields)
        if not schema_info:
            new_exclude_fields.append(BGVertex_JSON_SCHEMA_JSON_KEY)
        self.json_schema.exclude = new_exclude_fields
        result = self.json_schema.dump(self).data
        self.json_schema.exclude = old_exclude_fields
        return result

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        schema = cls.json_schema if json_schema_class is None else json_schema_class()
        deserialized_data = schema.load(data).data
        try:
            return cls(name=deserialized_data["name"])
        except KeyError:
            raise ValueError("No `name` key in supplied json data for vertex deserialization")

