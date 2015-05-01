# -*- coding: utf-8 -*-
from marshmallow import Schema, fields

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

INFINITY_VERTEX_IDENTIFIER = "__infinity"
BGVertex_JSON_SCHEMA_JSON_KEY = "_py__bg_vertex_json_schema"


class BGVertex(object):
    """ An base class that represents a vertex (node) with all associated information in a breakpoint graph data structure

    While class represents a base inheritance point for specific vertex implementations, it does implement most of
    business logic operations, that vertex shall support.

    While different type of vertices are to be represented with different python classes, they all have a string representation,
    which mainly relies one the `name` attribute.
    """

    # this class based variable is utilized to the purpose if separating vertex root name from any additions that would specify some special properties of the vertex
    # (like vertex classes, special properties, etc)
    NAME_SEPARATOR = "__"

    # each vertex is json serializable/deserializable and this is implemented with a help of marshmallow library and respective manually defined schema
    class BGVertexJSONSchema(Schema):
        name = fields.String(required=True, attribute="name")
        v_id = fields.Int(required=True, attribute="json_id")
        _py__bg_vertex_json_schema = fields.String(attribute="json_schema_name")

        def make_object(self, data):
            try:
                return BGVertex(name=data["name"])
            except KeyError:
                raise ValueError("No `name` key in supplied json data for vertex deserialization")

    # a schema class based variable with json deserialization schema
    # must be updated in all heirs, as schema specific method `make_object` specifies the type of deserialized object
    json_schema = BGVertexJSONSchema()

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        # all vertex are hashable objects and are uniquely defined by their name, thus a has value of vertex is just a hash value of its name
        return hash(self.name)

    def __eq__(self, other):
        # vertices are equal only if their class is equal as well as their names
        # in 99% of a time name is class specific and one can distinguish between vetices classes by only their names
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __getattr__(self, item):
        # this class serves as a stopper for all calls in form is_*_vertex, which is designed to test some combinatorial propoerties of vertex
        # base class does not belong to any specific group and thus answers `False` for all such calls
        # the rest of lookups is forwarded to the "next in mro chain"
        if item.startswith("is_") and item.endswith("_vertex"):
            return False
        return super().__getattribute__(item)

    @property
    def json_id(self):
        # a spicific vertex unique identifier that is utilized for aliasing vertices in json files (vertex might be references more than once), that is why
        # a reference to object by its json_id is used, rather than the full vertex object
        return hash(self)

    @property
    def json_schema_name(self):
        # each vertex is serialized with a help of some json schema (marshmallow powered), and information about such schema can be provided in
        # serialized vertex json object and further used to deserialized a vertex object into specific vertex class
        return self.json_schema.__class__.__name__

    def to_json(self, schema_info=True):
        # json serialization method that accounts for a possibility of excluding some schema specified fields from the result
        # also, since there are usually thousands of vertices serialized at the same time, no new schema object is created every time,
        # but rather some small monkey patching is performed with `exclude` field of json schema
        old_exclude_fields = self.json_schema.exclude
        new_exclude_fields = list(old_exclude_fields)
        if not schema_info:
            new_exclude_fields.append(BGVertex_JSON_SCHEMA_JSON_KEY)
        # monkey patch schema `exclude` attribute to ignore some fields in result json object
        self.json_schema.exclude = new_exclude_fields
        result = self.json_schema.dump(self).data
        # reverse the result of monkey patching
        self.json_schema.exclude = old_exclude_fields
        return result

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        # deserialization from json is performed by internal machinery of `make_object` method, that is invoked transparently
        # specific json schema class can be specified and used for deserialization
        schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return schema.load(data).data

    @staticmethod
    def get_vertex_class_from_vertex_name(string):
        # since every vertex even of different classes shall have a class specific `name` attribute, is is possible to distinguish between vertices classes
        # default value is BlockVertex, the most utilized vertex in the standard breakpoint graph
        result = BlockVertex
        data = string.split(BGVertex.NAME_SEPARATOR)
        suffixes = data[1:]
        if InfinityVertex.NAME_SUFFIX in suffixes:
            result = InfinityVertex
        return result

    @staticmethod
    def get_vertex_name_root(string):
        # as every vertex is represented by its name, some additional information about vertex class, type, etc. can be encoded into its name
        # such encoding is usually performed by appending some special suffixes to vertex name and utilizing `NAME_SEPARATOR` attribute
        return string.split(BGVertex.NAME_SEPARATOR)[0]


class BlockVertex(BGVertex):
    """ This class represents a special type of breakpoint graph vertex that correspond to a generic block extremity (gene/ synteny block/ etc.) """

    class BlockVertexJSONSchema(BGVertex.BGVertexJSONSchema):
        """ JSON schema for this class is redefined to tune the `make_object` method, that shall return `BlockVertex` instance, rather than `BGVertex` one """
        def make_object(self, data):
            try:
                return BlockVertex(name=data["name"])
            except KeyError:
                raise ValueError("No `name` key in supplied json data for vertex deserialization")

    # a new JSON schema is initialized and set of be used for all instance of `VertexClass`
    json_schema = BlockVertexJSONSchema()

    @property
    def is_regular_vertex(self):
        """ This class implements a property check for vertex to belong to class of regular vertices """
        return True


    @property
    def is_block_vertex(self):
        """ This class implements a property check for vertex to belong to a class of vertices, that correspond to extremities of genomic blocks"""
        return True

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        """ This class overwrites the from_json method thus, making sure, that if `from_json` is called from this class instance, it will provide its JSON schema as a default one """
        json_schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return super().from_json(data=data, json_schema_class=json_schema.__class__)


class InfinityVertex(BGVertex):
    """ This class represents a special type of breakpoint graph vertex that correspond to a generic extremity of genomic fragment (chromosome, scaffold, contig, etc.)"""

    class InfinityVertexJSONSchema(BGVertex.BGVertexJSONSchema):
        """ JSON Schema for this class is redefined to tune the `make_object` method, that shall return `InfinityVertex` instance, rather than a `BGVertex` one """
        def make_object(self, data):
            try:
                json_name = data["name"]
                name = json_name.split(InfinityVertex.NAME_SUFFIX)[0]
                return InfinityVertex(name=name)
            except KeyError:
                raise ValueError("No `name` key in supplied json data for vertex deserialization")

    # InfinityVertex instances have a special suffix in their name that is determined by a class variable `NAME_SUFFIX`
    NAME_SUFFIX = "infinity"

    # a setup for a new JSON schema is performed class-wise to be utilized by all instance of InfinityVertex
    json_schema = InfinityVertexJSONSchema()

    def __init__(self, name):
        # current class allows for a standard access to the `name` attribute, but performs transparent computation behind the scenes
        # so the name is stored in a private variable __name, and property `name` is implemented
        self.__name = None
        super().__init__(name=name)

    @property
    def name(self):
        """ access to classic name attribute is hidden by this property """
        return self.NAME_SEPARATOR.join([str(self.__name), self.NAME_SUFFIX])

    @name.setter
    def name(self, value):
        """When someone wants to set a new name for the `InfinityVertex` instance, it is transparently store into the `__name` attribute """
        self.__name = value

    @property
    def is_irregular_vertex(self):
        """ This class implements a property check for vertex to belong to a class of vertices, that correspond to extremities of genomic fragments """
        return True

    @property
    def is_infinity_vertex(self):
        """ This class implements a property check for vertex to belong to a class of vertices, that correspond to standard extremities of genomic fragments """
        return True

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        """ This class overwrites the from_json method, thus making sure that if `from_json` is called from this class instance, it will provide its JSON schema as a default one"""
        schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return super().from_json(data=data, json_schema_class=schema.__class__)


