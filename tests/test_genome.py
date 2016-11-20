__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest

from bg.genome import BGGenome, BGGenome_JSON_SCHEMA_JSON_KEY


class BGGenomeTestCase(unittest.TestCase):
    def test_initialization_incorrect(self):
        # empty genomes are not allowed, a name for genome is mandatory
        with self.assertRaises(TypeError):
            g = BGGenome()

    def test_initialization(self):
        # simple correct initialization
        g = BGGenome("name")
        self.assertEqual(g.name, "name")

    def test_hash(self):
        # hash of genome instance is proxies to hash value of its name
        g = BGGenome("name")
        self.assertEqual(hash(g), hash("name"))

    def test_json_id(self):
        # json id for genome is utilized when genome is serialized to json format and equals to hash value of genome instance
        g = BGGenome("name")
        json_id = g.json_id
        self.assertEqual(json_id, hash(g.name))
        self.assertTrue(isinstance(json_id, int))
        g.name = "name1"
        new_json_id = g.json_id
        self.assertEqual(new_json_id, hash(g.name))
        self.assertTrue(isinstance(json_id, int))
        self.assertNotEqual(json_id, new_json_id)

    def test__eq__(self):
        # two genome are called equal if they are both os same class and their hash values are equal
        g1 = BGGenome("name1")
        g2 = BGGenome("name2")
        self.assertNotEqual(g1, g2)
        g2.name = "name1"
        self.assertEqual(g1, g2)
        self.assertNotEqual(g1, 5)
        self.assertNotEqual(g1, "name1")
        self.assertNotEqual(g1, [g1])

    def test_json_serialization_no_subclassing(self):
        # genome can be serialized into json format keeping all important information
        g = BGGenome("name1")
        ref_result = {
            "name": "name1",
            "g_id": g.json_id
        }
        self.assertDictEqual(g.to_json(schema_info=False), ref_result)
        ref_result[BGGenome_JSON_SCHEMA_JSON_KEY] = g.json_schema_name
        self.assertDictEqual(g.to_json(), ref_result)

    def test_json_deserialization_no_subclassing(self):
        # simple case
        json_object = {
            "name": "name1",
            "g_id": 1
        }
        result = BGGenome.from_json(data=json_object)
        self.assertEqual(result.name, "name1")
        # g_id is not mandatory for genome deserialization itself, but is required by the supervising class
        self.assertEqual(BGGenome.from_json(data={"name": "name1"}).name, "name1")
        # BGGenome scheme info shall be ignored at this level, as it is supplied by the supervising class
        self.assertEqual(BGGenome.from_json(data={"name": "name1",
                                                  BGGenome_JSON_SCHEMA_JSON_KEY: "lalal"}).name, "name1")
        # error case when "name" is not present
        with self.assertRaises(ValueError):
            BGGenome.from_json(data={})

    def test_json_deserialization_subclassing(self):
        # being provided an explicit JSONSchema, it shall be utilized for json deserialization
        class BGGenomeJSONSchemaNameOptional(BGGenome.BGGenomeJSONSchema):
            def make_object(self, data):
                if "name" not in data:
                    data["name"] = "default_name"
                return super(BGGenomeJSONSchemaNameOptional, self).make_object(data=data)
        self.assertEqual(BGGenome.from_json(data={}, json_schema_class=BGGenomeJSONSchemaNameOptional).name, "default_name")

    def test__lt__(self):
        # genome is less than any non BGGenome instance
        # with other BGGenome instance it is compared by respective "name" attributes
        g1 = BGGenome("genome1")
        g2 = BGGenome("genome2")
        self.assertLess(g1, g2)
        self.assertGreater(g2, g1)
        g1 = BGGenome("genome1")
        g2 = BGGenome("genome")
        self.assertGreater(g1, g2)
        self.assertLess(g2, g1)
        # BGGenome is always smaller than non-BGGenome objects
        objects_to_compare_to = [1, (1,), [1], "a"]
        for object_to_compare_to in objects_to_compare_to:
            self.assertLess(g1, object_to_compare_to)
            self.assertLess(g2, object_to_compare_to)

    def test__le__(self):
        # Genome is considered less or equal to any other BGGenome is it is either less ("<" implementation
        # or equal (__eq__ implementation), than supplied argument
        g1 = BGGenome("genome1")
        g2 = BGGenome("genome1")
        self.assertLessEqual(g1, g2)
        self.assertLessEqual(g2, g1)
        self.assertTrue(g1 <= g2 <= g1)
        g3 = BGGenome("genome")
        self.assertLessEqual(g3, g1)
        self.assertLessEqual(g3, g1)


if __name__ == '__main__':
    unittest.main()
