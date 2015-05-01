# -*- coding: utf-8 -*-
from marshmallow import Schema, fields

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

# module wide constant, that is utilized for json dict key creation
BGGenome_JSON_SCHEMA_JSON_KEY = "_py__bg_genome_json_schema"


class BGGenome(object):
    """ A class that represent a genome object for the breakpoint graph

     For purposes of breakpoint graph no additional information about genome is needed, except its name, that is used in various
     algorithmic tasks (multicolor splitting, tree traversing, etc)
    """
    class BGGenomeJSONSchema(Schema):
        """ a JSON schema powered by marshmallow library to serialize/deserialize genome object into/from JSON format
        """
        _py__bg_genome_json_schema = fields.String(attribute="json_schema_name")
        g_id = fields.Integer(attribute="json_id")
        name = fields.String()

        def make_object(self, data):
            if "name" not in data:
                raise ValueError("Error during genome serialization. \"name\" key is not present in json object")
            name = data["name"]
            return BGGenome(name=name)

    # class wide variable for json serialization/deserialization. Created once for a whole class, as thousands of objects
    # undergo serialization / deserialization, and schema instantiation in each case would require additional resources
    json_schema = BGGenomeJSONSchema()

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        """ Two genomes a called equal if they are of same class and their hash values are equal to each other """
        if not isinstance(other, BGGenome):
            return False
        return hash(self) == hash(other)

    def __hash__(self):
        """ Since for breakpoint graph purposes distinction between genomes is made purely by their name, hash value of genome
         is proxied to hash value of genomes name
         """
        return hash(self.name)

    @property
    def json_id(self):
        """ A genome is references multiple times, as for example in multicolor object, and such reference is done by genome
        unique json id.
        """
        return hash(self)

    @property
    def json_schema_name(self):
        """ When genome is serialized information about JSON schema of such serialization can be recorded,
        and this property provides access to it
        """
        return self.json_schema.__class__.__name__

    def to_json(self, schema_info=True):
        """ JSON serialization method that accounts for a possibility of field filtration and schema specification """
        old_exclude_fields = self.json_schema.exclude
        new_exclude_fields = list(old_exclude_fields)
        if not schema_info:
            new_exclude_fields.append(BGGenome_JSON_SCHEMA_JSON_KEY)
        # monkey patch schema `exclude` attribute to ignore some fields in result json object
        self.json_schema.exclude = new_exclude_fields
        result = self.json_schema.dump(self).data
        # reverse the result of monkey patching
        self.json_schema.exclude = old_exclude_fields
        return result

    @classmethod
    def from_json(cls, data, json_schema_class=None):
        """ JSON deserialization method that retrieves a genome instance from its json representation

        If specific json schema is provided, it is utilized, and if not, a class specific is used
        """
        schema = cls.json_schema if json_schema_class is None else json_schema_class()
        return schema.load(data).data

    def __lt__(self, other):
        """ Genomes are ordered according to lexicographical ordering of their names """
        if not isinstance(other, BGGenome):
            return True
        return self.name < other.name

    def __le__(self, other):
        """ Genomes are ordered according to lexicographical ordering of their names """
        return self < other or self == other