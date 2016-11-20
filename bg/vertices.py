# -*- coding: utf-8 -*-
from bisect import bisect_left

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
        self._name = None
        self.name = name

    @property
    def name(self):
        return str(self._name)

    @name.setter
    def name(self, value):
        self._name = value

    def __hash__(self):
        # all vertex are hashable objects and are uniquely defined by their name, thus a has value of vertex is just a hash value of its name
        return hash(self.name)

    def __eq__(self, other):
        # vertices are equal only if their class is equal as well as their names
        # in 99% of a time name is class specific and one can distinguish between vetices classes by only their names
        if not isinstance(other, BGVertex):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other=other)

    def __getattr__(self, item):
        # this class serves as a stopper for all calls in form is_*_vertex, which is designed to test some combinatorial propoerties of vertex
        # base class does not belong to any specific group and thus answers `False` for all such calls
        # the rest of lookups is forwarded to the "next in mro chain"
        if item.startswith("is_") and item.endswith("_vertex"):
            return False
        return super(BGVertex, self).__getattribute__(item)

    def __str__(self):
        return self.name

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
        if InfinityVertex.NAME_SUFFIX in string.split(BGVertex.NAME_SEPARATOR)[1:]:
            return TaggedInfinityVertex
        else:
            return TaggedBlockVertex

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

    def __init__(self, name, mate_vertex=None):
        super(BlockVertex, self).__init__(name=name)
        self.mate_vertex = mate_vertex

    @property
    def is_regular_vertex(self):
        """ This class implements a property check for vertex to belong to class of regular vertices """
        return True

    @property
    def block_name(self):
        if self.is_block_vertex:
            if self.is_tail_vertex or self.is_head_vertex:
                return self._name[:-1]
            else:
                return self._name

    @property
    def is_block_vertex(self):
        """ This class implements a property check for vertex to belong to a class of vertices, that correspond to extremities of genomic blocks"""
        return True

    @property
    def is_head_vertex(self):
        return self.is_block_vertex and self._name.endswith("h")

    @property
    def is_tail_vertex(self):
        return self.is_block_vertex and self._name.endswith("t")

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        """ This class overwrites the from_json method thus, making sure, that if `from_json` is called from this class instance, it will provide its JSON schema as a default one """
        json_schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return super(BlockVertex, cls).from_json(data=data, json_schema_class=json_schema.__class__)


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
        super(InfinityVertex, self).__init__(name=name)

    @property
    def name(self):
        """ access to classic name attribute is hidden by this property """
        return self.NAME_SEPARATOR.join([super(InfinityVertex, self).name, self.NAME_SUFFIX])

    @name.setter
    def name(self, value):
        """When someone wants to set a new name for the `InfinityVertex` instance, it is transparently store into the `__name` attribute """
        self._name = value

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
        return super(InfinityVertex, cls).from_json(data=data, json_schema_class=schema.__class__)


class TaggedVertex(BGVertex):
    class TaggedVertexJSONSchema(BGVertex.BGVertexJSONSchema):

        def make_object(self, data):
            predefined_object_class = getattr(self, "object_class", None)
            object_class = TaggedVertex if predefined_object_class is None else predefined_object_class
            try:
                json_name = data["name"]
                split_name = json_name.split(TaggedVertex.NAME_SEPARATOR)
                root = split_name[0]
                tags = list(filter(lambda name_part: TaggedVertex.TAG_SEPARATOR in name_part, split_name[1:]))
                tags = [entry.split(TaggedVertex.TAG_SEPARATOR) for entry in tags]
                result = object_class(name=root)
                result.tags = sorted(tags)
                return result
            except KeyError:
                raise ValueError("No `name` key in supplied json data for vertex deserialization")

    TAG_SEPARATOR = ":"

    json_schema = TaggedVertexJSONSchema()

    def __init__(self, name):
        self.tags = []
        super(TaggedVertex, self).__init__(name=name)

    @property
    def is_tagged_vertex(self):
        return True

    @property
    def name(self):
        """ access to classic name attribute is hidden by this property """
        return self.NAME_SEPARATOR.join([super(TaggedVertex, self).name] + self.get_tags_as_list_of_strings())

    def get_tags_as_list_of_strings(self):
        return [self.TAG_SEPARATOR.join([str(tag), str(value)]) for tag, value in self.tags]

    @name.setter
    def name(self, value):
        """ shared "protected" variable for the name storing attribute """
        self._name = value

    def add_tag(self, tag, value):
        """ as tags are kept in a sorted order, a bisection is a fastest way to identify a correct position
        of or a new tag to be added. An additional check is required to make sure w don't add duplicates
        """
        index = bisect_left(self.tags, (tag, value))
        contains = False
        if index < len(self.tags):
            contains = self.tags[index] == (tag, value)
        if not contains:
            self.tags.insert(index, (tag, value))

    def __getattr__(self, item):
        """  """
        if item.startswith("is_") and item.endswith("_vertex"):
            tag = item[3:-7]
            index = bisect_left([tag_name for tag_name, _ in self.tags], tag)
            if index < len(self.tags):
                return self.tags[index][0] == tag
        return super(TaggedVertex, self).__getattr__(item)

    def remove_tag(self, tag, value, silent_fail=False):
        """ we try to remove supplied pair tag -- value, and if does not exist outcome depends on the silent_fail flag """
        try:
            self.tags.remove((tag, value))
        except ValueError as err:
            if not silent_fail:
                raise err

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        """ This class overwrites the from_json method, thus making sure that if `from_json` is called from this class instance, it will provide its JSON schema as a default one"""
        schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return super(TaggedVertex, cls).from_json(data=data, json_schema_class=schema.__class__)


class TaggedBlockVertex(BlockVertex, TaggedVertex):
    class TaggedBlockVertexJSONSchema(TaggedVertex.TaggedVertexJSONSchema, BlockVertex.BlockVertexJSONSchema):
        def make_object(self, data):
            setattr(self, "object_class", TaggedBlockVertex)
            return super(TaggedBlockVertex.TaggedBlockVertexJSONSchema, self).make_object(data)

    json_schema = TaggedBlockVertexJSONSchema()


class TaggedInfinityVertex(InfinityVertex, TaggedVertex):
    class TaggedInfinityVertexJSONSchema(TaggedVertex.TaggedVertexJSONSchema, InfinityVertex.InfinityVertexJSONSchema):
        def make_object(self, data):
            setattr(self, "object_class", TaggedInfinityVertex)
            return super(TaggedInfinityVertex.TaggedInfinityVertexJSONSchema, self).make_object(data)

    json_schema = TaggedInfinityVertexJSONSchema()
