# -*- coding: utf-8 -*-
from marshmallow import Schema, fields

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

INFINITY_VERTEX_IDENTIFIER = "__infinity"
BGVertex_JSON_SCHEMA_JSON_KEY = "_py__bg_vertex_json_schema"


class BGVertex(object):

    NAME_SEPARATOR = "__"

    class BGVertexJSONSchema(Schema):
        name = fields.String(required=True, attribute="name")
        v_id = fields.Int(required=True, attribute="json_id")
        _py__bg_vertex_json_schema = fields.String(attribute="json_schema_name")

        def make_object(self, data):
            try:
                return BGVertex(name=data["name"])
            except KeyError:
                raise ValueError("No `name` key in supplied json data for vertex deserialization")

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
        return schema.load(data).data

    @staticmethod
    def get_vertex_class_from_vertex_name(string):
        result = BlockVertex
        data = string.split(BGVertex.NAME_SEPARATOR)
        suffixes = data[1:]
        if InfinityVertex.NAME_SUFFIX in suffixes:
            result = InfinityVertex
        return result

    @staticmethod
    def get_vertex_name_root(string):
        return string.split(BGVertex.NAME_SEPARATOR)[0]


class BlockVertex(BGVertex):

    class BlockVertexJSONSchema(BGVertex.BGVertexJSONSchema):

        def make_object(self, data):
            try:
                return BlockVertex(name=data["name"])
            except KeyError:
                raise ValueError("No `name` key in supplied json data for vertex deserialization")

    json_schema = BlockVertexJSONSchema()

    @property
    def is_regular_vertex(self):
        return True

    @property
    def is_block_vertex(self):
        return True

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        json_schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return super().from_json(data=data, json_schema_class=json_schema.__class__)


class InfinityVertex(BGVertex):

    class InfinityVertexJSONSchema(BGVertex.BGVertexJSONSchema):
        def make_object(self, data):
            try:
                json_name = data["name"]
                name = json_name.split(InfinityVertex.NAME_SUFFIX)[0]
                return InfinityVertex(name=name)
            except KeyError:
                raise ValueError("No `name` key in supplied json data for vertex deserialization")

    NAME_SUFFIX = "infinity"

    json_schema = InfinityVertexJSONSchema()

    def __init__(self, name):
        self.__name = None
        super().__init__(name=name)

    @property
    def name(self):
        return self.NAME_SEPARATOR.join([str(self.__name), self.NAME_SUFFIX])

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def is_irregular_vertex(self):
        return True

    @property
    def is_infinity_vertex(self):
        return True

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return super().from_json(data=data, json_schema_class=schema.__class__)


