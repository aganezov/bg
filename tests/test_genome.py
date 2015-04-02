__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.genome import BGGenome, BGGenome_JSON_SCHEMA_JSON_KEY


class BGGenomeTestCase(unittest.TestCase):
    def test_initialization_incorrect(self):
        with self.assertRaises(TypeError):
            g = BGGenome()

    def test_initialization(self):
        g = BGGenome("name")
        self.assertEqual(g.name, "name")

    def test_hash(self):
        g = BGGenome("name")
        self.assertEqual(hash(g), hash("name"))

    def test_json_id(self):
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
        g1 = BGGenome("name1")
        g2 = BGGenome("name2")
        self.assertNotEqual(g1, g2)
        g2.name = "name1"
        self.assertEqual(g1, g2)
        self.assertNotEqual(g1, 5)
        self.assertNotEqual(g1, "name1")
        self.assertNotEqual(g1, [g1])

    def test_json_serialization_no_subclassing(self):
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
        class BGGenomeJSONSchemaNameOptional(BGGenome.BGGenomeJSONSchema):
            def make_object(self, data):
                if "name" not in data:
                    data["name"] = "default_name"
                return super().make_object(data=data)
        self.assertEqual(BGGenome.from_json(data={}, json_schema_class=BGGenomeJSONSchemaNameOptional).name, "default_name")


if __name__ == '__main__':
    unittest.main()
