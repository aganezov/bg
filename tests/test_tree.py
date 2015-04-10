# -*- coding: utf-8 -*-
from bg.genome import BGGenome
from bg.tree import BGTree, NewickReader, DEFAULT_EDGE_LENGTH

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest


class BGTreeTestCase(unittest.TestCase):
    def setUp(self):
        v1, v2, v3, v4 = BGGenome("v1"), BGGenome("v2"), BGGenome("v3"), BGGenome("v4")
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4

    def test_empty_tree_initialization(self):
        tree = BGTree()
        self.assertIsNone(tree.root)
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 0)
        self.assertEqual(len(list(tree.edges())), 0)

    def test_add_genome(self):
        tree = BGTree()
        tree.add_node(BGGenome("genome"))
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 1)
        self.assertEqual(len(list(tree.edges())), 0)

    def test_edge_length(self):
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, edge_length=5)
        self.assertEqual(tree.edge_length(vertex1=self.v1, vertex2=self.v2), 5)
        self.assertEqual(tree.edge_length(vertex1=self.v2, vertex2=self.v1), 5)
        with self.assertRaises(ValueError):
            tree.edge_length(vertex1=self.v1, vertex2=self.v3)
        with self.assertRaises(ValueError):
            tree.edge_length(vertex1=self.v3, vertex2=self.v4)
        with self.assertRaises(ValueError):
            tree.edge_length(vertex1=self.v3, vertex2=self.v4)

    def test_edge_wgd_information(self):
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, wgd_events=5)
        tree.add_edge(vertex1=self.v1, vertex2=self.v3)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v2, vertex2=self.v1), 5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v3), 0)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v3, vertex2=self.v1), 0)
        with self.assertRaises(ValueError):
            tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v4)
        with self.assertRaises(ValueError):
            tree.edge_wgd_count(vertex1=self.v3, vertex2=self.v4)

    def test_add_edge(self):
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 2)
        self.assertEqual(len(list(tree.edges())), 1)
        self.assertEqual(tree.edge_length(self.v1, self.v2), 1)

    def test_add_edge_explicit_edge_length(self):
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, edge_length=5)
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 2)
        self.assertEqual(len(list(tree.edges())), 1)
        self.assertEqual(tree.edge_length(self.v1, self.v2), 5)

    def test_add_edge_explicit_wgd(self):
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, wgd_events=5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v2, vertex2=self.v1), 5)

    def test_has_edge(self):
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        tree.add_node(self.v3)
        self.assertTrue(tree.has_edge(self.v1, self.v2))
        self.assertTrue(tree.has_edge(self.v2, self.v1))
        self.assertFalse(tree.has_edge(self.v1, self.v3))
        self.assertFalse(tree.has_edge(self.v3, self.v1))
        self.assertFalse(tree.has_edge(self.v3, self.v2))
        self.assertFalse(tree.has_edge(self.v2, self.v3))
        self.assertFalse(tree.has_edge(self.v1, self.v4))
        self.assertFalse(tree.has_edge(self.v4, self.v1))

    def test_has_node(self):
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        tree.add_node(self.v3)
        self.assertTrue(tree.has_node(self.v1))
        self.assertTrue(tree.has_node(self.v2))
        self.assertTrue(tree.has_node(self.v3))
        self.assertFalse(tree.has_node(self.v4))

    def test_assign_root(self):
        tree = BGTree()
        self.assertIsNone(tree.root)
        with self.assertRaises(ValueError):
            tree.root = self.v1
        tree.add_node(self.v1)
        tree.root = self.v1
        self.assertEqual(tree.root, self.v1)

    def test_append_tree(self):
        tree1 = BGTree()
        tree2 = BGTree()
        tree1.add_edge(vertex1=self.v1, vertex2=self.v2)
        tree2.add_edge(vertex1=self.v2, vertex2=self.v3)
        self.assertTrue(tree1.is_valid_tree)
        self.assertTrue(tree2.is_valid_tree)
        tree1.append(tree=tree2)
        #####
        self.assertTrue(tree1.is_valid_tree)
        self.assertEqual(len(list(tree1.nodes())), 3)
        self.assertEqual(len(list(tree1.edges())), 2)
        self.assertTrue(tree1.has_edge(vertex1=self.v3, vertex2=self.v2))
        self.assertTrue(tree1.has_edge(vertex1=self.v1, vertex2=self.v2))
        #####
        self.assertTrue(tree2.is_valid_tree)
        self.assertEqual(len(list(tree2.nodes())), 2)
        self.assertEqual(len(list(tree2.edges())), 1)

    def test_set_wgd_count_correct(self):
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 0)
        tree.set_wgd_count(vertex1=self.v1, vertex2=self.v2, wgd_count=2)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 2)
        tree.set_wgd_count(vertex1=self.v2, vertex2=self.v1, wgd_count=3)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 3)

    def test_set_wgd_count_incorrect(self):
        # only for existing edges such setup if possible
        tree = BGTree()
        with self.assertRaises(ValueError):
            self.assertEqual(tree.set_wgd_count(vertex1=self.v1, vertex2=self.v2, wgd_count=2), 2)
        # only positive integers are allowed as values for whole genome duplication count
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        incorrect_counts = [0.5, "a", (1,), [1]]
        for incorrect_count in incorrect_counts:
            with self.assertRaises(ValueError):
                tree.set_wgd_count(vertex1=self.v1, vertex2=self.v2, wgd_count=incorrect_count)

    def test_set_edge_length(self):
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        tree.set_edge_length(vertex1=self.v1, vertex2=self.v2, edge_length=3)
        self.assertEqual(tree.edge_length(vertex1=self.v1, vertex2=self.v2), 3)
        tree.set_edge_length(vertex1=self.v1, vertex2=self.v2, edge_length=5)
        self.assertEqual(tree.edge_length(vertex1=self.v2, vertex2=self.v1), 5)

    def test_set_edge_length_incorrect(self):
        # only for existing edges such setup is possible
        tree = BGTree()
        with self.assertRaises(ValueError):
            tree.set_edge_length(vertex1=self.v1, vertex2=self.v2, edge_length=3)


class NewickParserTestCase(unittest.TestCase):
    def test_parse_simple_node_no_edge_length_correct(self):
        # simple node must be a leaf, and all leafs represent genomes
        node_string = "genome"
        node, edge_length = NewickReader.parse_simple_node(node_string)
        self.assertEqual(edge_length, DEFAULT_EDGE_LENGTH)
        self.assertTrue(isinstance(node, BGGenome))
        self.assertEqual(node, BGGenome("genome"))
        node_string = "genome:"
        node, edge_length = NewickReader.parse_simple_node(node_string)
        self.assertEqual(edge_length, DEFAULT_EDGE_LENGTH)
        self.assertTrue(isinstance(node, BGGenome))
        self.assertEqual(node, BGGenome("genome"))

    def test_parse_simple_incorrect_empty_node(self):
        # node name can not be empty
        node_string = ""
        with self.assertRaises(ValueError):
            NewickReader.parse_simple_node(node_string)

    def test_parse_simple_incorrect_multi_semicolon(self):
        node_string = "genome:5:5"
        with self.assertRaises(ValueError):
            NewickReader.parse_simple_node(node_string)

    def test_parse_simple_node_with_edge_length_correct(self):
        # case with correct edge_length `int`
        node_strings = [
            " genome:5",
            "genome :5",
            " genome :5"
        ]
        for node_string in node_strings:
            node, edge_length = NewickReader.parse_simple_node(node_string)
            self.assertEqual(edge_length, 5)
            self.assertTrue(isinstance(node, BGGenome))
            self.assertEqual(node, BGGenome("genome"))
        # case with correct edge_length `double`
        node_strings = [
            "genome:2.1",
            "genome: 2.1",
            "genome:2.1 ",
            "genome: 2.1 "
        ]
        for node_string in node_strings:
            node, edge_length = NewickReader.parse_simple_node(node_string)
            self.assertEqual(edge_length, 2.1)
            self.assertTrue(isinstance(node, BGGenome))
            self.assertEqual(node, BGGenome("genome"))

    def test_parse_simple_node_incorrect_edge_length(self):
        incorrectly_formatted_strings = [
            "genome:5.1.1",
            "genome:5a",
            "genome:5/2",
            "genome:test",
            "genome:5.2a"
        ]
        for node_string in incorrectly_formatted_strings:
            with self.assertRaises(ValueError):
                NewickReader.parse_simple_node(node_string)

    def test_separate_into_same_level_nodes_correct(self):
        # empty string shall be parsed into a single entry list with empty string
        data_string = ""
        result_list = NewickReader.separate_into_same_level_nodes(data_string)
        self.assertListEqual(result_list, [""])
        # single node string must be parsed into a single list entry with node info
        data_strings = ["a", "a:5" "a:5.1"]
        for data_string in data_strings:
            self.assertListEqual(NewickReader.separate_into_same_level_nodes(data_string), [data_string])
        # multiple terminal nodes must be parsed into a list of respective information about nodes
        data_string = " a,   b:5, c:2.1,d    "
        ref_list = ["a", "b:5", "c:2.1", "d"]
        result_list = NewickReader.separate_into_same_level_nodes(data_string)
        self.assertListEqual(result_list, ref_list)
        # multiple terminal nodes + non-terminal subtree
        data_string = " a,  b:3.1, (c,(d,e)f)g:1, (h,i)j:2.1   "
        ref_list = ["a", "b:3.1", "(c,(d,e)f)g:1", "(h,i)j:2.1"]
        result_list = NewickReader.separate_into_same_level_nodes(data_string)
        self.assertListEqual(result_list, ref_list)
        # a single subtree as a node
        data_string = "(a,b)"
        ref_list = ["(a,b)"]
        self.assertListEqual(NewickReader.separate_into_same_level_nodes(data_string), ref_list)

    def test_separate_into_same_level_nodes_incorrect(self):
        error_data_string = [
            ",a,b",
            "a,,b",
            "a,b,,",
            "(),,a",
            ",(),a",
            ",(),,"
        ]
        for data_string in error_data_string:
            with self.assertRaises(ValueError):
                NewickReader.separate_into_same_level_nodes(data_string)

    def test_is_non_terminal_subtree(self):
        data_string = "a"
        self.assertFalse(NewickReader.is_non_terminal_subtree(data_string))
        data_string = "(a,b)"
        self.assertTrue(NewickReader.is_non_terminal_subtree(data_string))
        data_string = "(a,b)c"
        self.assertTrue(NewickReader.is_non_terminal_subtree(data_string))
        data_string = "(a,c):5"
        self.assertTrue(NewickReader.is_non_terminal_subtree(data_string))
        data_string = "(a,c)c:5"
        self.assertTrue(NewickReader.is_non_terminal_subtree(data_string))

    def test_parse_tree_root(self):
        data_string = "()a"
        subtree_string, root_string = NewickReader.tree_node_separation(data_string)
        self.assertEqual(subtree_string, "()")
        self.assertEqual(root_string, "a")
        data_string = "()"
        subtree_string, root_string = NewickReader.tree_node_separation(data_string)
        self.assertEqual(subtree_string, "()")
        self.assertEqual(root_string, "")
        data_string = "()a:5"
        subtree_string, root_string = NewickReader.tree_node_separation(data_string)
        self.assertEqual(subtree_string, "()")
        self.assertEqual(root_string, "a:5")
        data_string = "():5"
        subtree_string, root_string = NewickReader.tree_node_separation(data_string)
        self.assertEqual(subtree_string, "()")
        self.assertEqual(root_string, ":5")

    def test_from_string_correct(self):
        # simplest valid test case with a single node
        data_string = "a;"
        tree = NewickReader.from_string(data_string=data_string)
        self.assertEqual(tree.root, BGGenome("a"))
        self.assertEqual(len(list(tree.nodes())), 1)
        self.assertEqual(len(list(tree.edges())), 0)
        # non-terminal nodes, if labeled explicitly are saved as string entries
        data_string = "(a,b)c;"
        tree = NewickReader.from_string(data_string)
        self.assertTrue(isinstance(tree, BGTree))
        self.assertTrue(tree.is_valid_tree)
        self.assertTrue(tree.has_edge(BGGenome("a"), "c"))
        self.assertTrue(tree.has_edge(BGGenome("b"), "c"))
        self.assertEqual(tree.edge_length(BGGenome("a"), "c"), DEFAULT_EDGE_LENGTH)
        self.assertEqual(tree.edge_length(BGGenome("b"), "c"), DEFAULT_EDGE_LENGTH)
        self.assertEqual(tree.edge_wgd_count(BGGenome("a"), "c"), 0)
        self.assertEqual(tree.edge_wgd_count(BGGenome("b"), "c"), 0)
        self.assertEqual(tree.root, "c")
        # non-terminal nodes, if not labeled explicitly are assigned iteratively increased integer values, casted to str
        # since processing is left-to-right, testing for implicitly assigned values can be deterministic
        data_string = "((a,b:5),(c,d):.5);"
        tree = NewickReader.from_string(data_string)
        ga, gb, gc, gd = BGGenome("a"), BGGenome("b"), BGGenome("c"), BGGenome("d")
        self.assertTrue(isinstance(tree, BGTree))
        self.assertTrue(tree.is_valid_tree)
        self.assertTrue(tree.has_edge("2", "1"))
        self.assertTrue(tree.has_edge("3", "1"))
        self.assertTrue(tree.has_edge("2", "1"))
        self.assertTrue(tree.has_edge(ga, "2"))
        self.assertTrue(tree.has_edge(gb, "2"))
        self.assertTrue(tree.has_edge(gc, "3"))
        self.assertTrue(tree.has_edge(gd, "3"))
        self.assertEqual(tree.edge_length(ga, "2"), DEFAULT_EDGE_LENGTH)
        self.assertEqual(tree.edge_length(gb, "2"), 5)
        self.assertEqual(tree.edge_length(gc, "3"), DEFAULT_EDGE_LENGTH)
        self.assertEqual(tree.edge_length(gd, "3"), DEFAULT_EDGE_LENGTH)
        self.assertEqual(tree.edge_length("1", "2"), DEFAULT_EDGE_LENGTH)
        self.assertEqual(tree.edge_length("1", "3"), 0.5)
        # another example
        data_string = "(B:6.0,(A:5.0,C:3.0,E:4.0)Ancestor1:5.0,D:11.0);"
        tree = NewickReader.from_string(data_string)
        ga, gb, gc, gd, ge, anc = BGGenome("A"), BGGenome("B"), BGGenome("C"), BGGenome("D"), BGGenome("E"), "Ancestor1"
        self.assertTrue(isinstance(tree, BGTree))
        self.assertTrue(tree.is_valid_tree)
        self.assertTrue(tree.has_edge(gd, "1"))
        self.assertTrue(tree.has_edge(anc, "1"))
        self.assertTrue(tree.has_edge(gb, "1"))
        self.assertTrue(tree.has_edge(ga, anc))
        self.assertTrue(tree.has_edge(gc, anc))
        self.assertTrue(tree.has_edge(ge, anc))
        self.assertEqual(tree.edge_length(anc, "1"), 5.0)
        self.assertEqual(tree.edge_length(gd, "1"), 11.0)
        self.assertEqual(tree.edge_length(gb, "1"), 6.0)
        self.assertTrue(tree.edge_length(ga, anc), 5.0)
        self.assertTrue(tree.edge_length(gc, anc), 3.0)
        self.assertTrue(tree.edge_length(ge, anc), 4.0)

    def test_from_string_incorrect(self):
        # multiple top level nodes
        data_string = "a,(c,d)b;"
        with self.assertRaises(ValueError):
            NewickReader.from_string(data_string=data_string)
        # empty terminal node
        data_strings = ["(a,);", ";"]
        for data_string in data_strings:
            with self.assertRaises(ValueError):
                NewickReader.from_string(data_string=data_string)


if __name__ == '__main__':
    unittest.main()
