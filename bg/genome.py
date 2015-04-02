# -*- coding: utf-8 -*-
from marshmallow import Schema, fields

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

BGGenome_JSON_SCHEMA_JSON_KEY = "_py__bg_genome_json_schema"


class BGGenome(object):
    class BGGenomeJSONSchema(Schema):
        _py__bg_genome_json_schema = fields.String(attribute="json_schema_name")
        g_id = fields.Integer(attribute="json_id")
        name = fields.String()

        def make_object(self, data):
            if "name" not in data:
                raise ValueError("Error during genome serialization. \"name\" key is not present in json object")
            name = data["name"]
            return BGGenome(name=name)

    json_schema = BGGenomeJSONSchema()

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, BGGenome):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

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
            new_exclude_fields.append(BGGenome_JSON_SCHEMA_JSON_KEY)
        self.json_schema.exclude = new_exclude_fields
        result = self.json_schema.dump(self).data
        self.json_schema.exclude = old_exclude_fields
        return result

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return schema.load(data).data