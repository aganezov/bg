# -*- coding: utf-8 -*-
from bg.genome import BGGenome
from bg.tree import Tree, NewickParser, DEFAULT_BRANCH_LENGTH

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest


class TreeTestCase(unittest.TestCase):
    def setUp(self):
        v1, v2, v3, v4 = BGGenome("v1"), BGGenome("v2"), BGGenome("v3"), BGGenome("v4")
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4

    def test_empty_tree_initialization(self):
        tree = Tree()
        self.assertIsNone(tree.root)
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 0)
        self.assertEqual(len(list(tree.edges())), 0)

    def test_add_genome(self):
        tree = Tree()
        tree.add_node(BGGenome("genome"))
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 1)
        self.assertEqual(len(list(tree.edges())), 0)

    def test_edge_branch_length(self):
        tree = Tree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, branch_length=5)
        self.assertEqual(tree.edge_length(vertex1=self.v1, vertex2=self.v2), 5)
        self.assertEqual(tree.edge_length(vertex1=self.v2, vertex2=self.v1), 5)
        with self.assertRaises(ValueError):
            tree.edge_length(vertex1=self.v1, vertex2=self.v3)
        with self.assertRaises(ValueError):
            tree.edge_length(vertex1=self.v3, vertex2=self.v4)
        with self.assertRaises(ValueError):
            tree.edge_length(vertex1=self.v3, vertex2=self.v4)

    def test_edge_wgd_information(self):
        tree = Tree()
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
        tree = Tree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 2)
        self.assertEqual(len(list(tree.edges())), 1)
        self.assertEqual(tree.edge_length(self.v1, self.v2), 1)

    def test_add_edge_explicit_branch_length(self):
        tree = Tree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, branch_length=5)
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 2)
        self.assertEqual(len(list(tree.edges())), 1)
        self.assertEqual(tree.edge_length(self.v1, self.v2), 5)

    def test_add_edge_explicit_wgd(self):
        tree = Tree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, wgd_events=5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v2, vertex2=self.v1), 5)

    def test_has_edge(self):
        tree = Tree()
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
        tree = Tree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        tree.add_node(self.v3)
        self.assertTrue(tree.has_node(self.v1))
        self.assertTrue(tree.has_node(self.v2))
        self.assertTrue(tree.has_node(self.v3))
        self.assertFalse(tree.has_node(self.v4))

    def test_assign_root(self):
        tree = Tree()
        self.assertIsNone(tree.root)
        with self.assertRaises(ValueError):
            tree.root = self.v1
        tree.add_node(self.v1)
        tree.root = self.v1
        self.assertEqual(tree.root, self.v1)

    def test_append_tree(self):
        tree1 = Tree()
        tree2 = Tree()
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


class NewickParserTestCase(unittest.TestCase):
    def test_parse_simple_node_no_branch_length_correct(self):
        # simple node must be a leaf, and all leafs represent genomes
        node_string = "genome"
        node, branch_length = NewickParser.parse_simple_node(node_string)
        self.assertEqual(branch_length, DEFAULT_BRANCH_LENGTH)
        self.assertTrue(isinstance(node, BGGenome))
        self.assertEqual(node, BGGenome("genome"))
        node_string = "genome:"
        node, branch_length = NewickParser.parse_simple_node(node_string)
        self.assertEqual(branch_length, DEFAULT_BRANCH_LENGTH)
        self.assertTrue(isinstance(node, BGGenome))
        self.assertEqual(node, BGGenome("genome"))

    def test_parse_simple_incorrect_empty_node(self):
        # node name can not be empty
        node_string = ""
        with self.assertRaises(ValueError):
            NewickParser.parse_simple_node(node_string)

    def test_parse_simple_incorrect_multi_semicolon(self):
        node_string = "genome:5:5"
        with self.assertRaises(ValueError):
            NewickParser.parse_simple_node(node_string)

    def test_parse_simple_node_with_branch_length_correct(self):
        # case with correct branch_length `int`
        node_strings = [
            " genome:5",
            "genome :5",
            " genome :5"
        ]
        for node_string in node_strings:
            node, branch_length = NewickParser.parse_simple_node(node_string)
            self.assertEqual(branch_length, 5)
            self.assertTrue(isinstance(node, BGGenome))
            self.assertEqual(node, BGGenome("genome"))
        # case with correct branch_length `double`
        node_strings = [
            "genome:2.1",
            "genome: 2.1",
            "genome:2.1 ",
            "genome: 2.1 "
        ]
        for node_string in node_strings:
            node, branch_length = NewickParser.parse_simple_node(node_string)
            self.assertEqual(branch_length, 2.1)
            self.assertTrue(isinstance(node, BGGenome))
            self.assertEqual(node, BGGenome("genome"))

    def test_parse_simple_node_incorrect_branch_length(self):
        incorrectly_formatted_strings = [
            "genome:5.1.1",
            "genome:5a",
            "genome:5/2",
            "genome:test",
            "genome:5.2a"
        ]
        for node_string in incorrectly_formatted_strings:
            with self.assertRaises(ValueError):
                NewickParser.parse_simple_node(node_string)

    def test_separate_into_same_level_nodes_correct(self):
        # empty string shall be parsed into a single entry list with empty string
        data_string = ""
        result_list = NewickParser.separate_into_same_level_nodes(data_string)
        self.assertListEqual(result_list, [""])
        # single node string must be parsed into a single list entry with node info
        data_strings = ["a", "a:5" "a:5.1"]
        for data_string in data_strings:
            self.assertListEqual(NewickParser.separate_into_same_level_nodes(data_string), [data_string])
        # multiple terminal nodes must be parsed into a list of respective information about nodes
        data_string = " a,   b:5, c:2.1,d    "
        ref_list = ["a", "b:5", "c:2.1", "d"]
        result_list = NewickParser.separate_into_same_level_nodes(data_string)
        self.assertListEqual(result_list, ref_list)
        # multiple terminal nodes + non-terminal subtree
        data_string = " a,  b:3.1, (c,(d,e)f)g:1, (h,i)j:2.1   "
        ref_list = ["a", "b:3.1", "(c,(d,e)f)g:1", "(h,i)j:2.1"]
        result_list = NewickParser.separate_into_same_level_nodes(data_string)
        self.assertListEqual(result_list, ref_list)

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
                NewickParser.separate_into_same_level_nodes(data_string)

    def test_is_non_terminal_subtree(self):
        data_string = "a"
        self.assertFalse(NewickParser.is_non_terminal_subtree(data_string))
        data_string = "(a,b)"
        self.assertTrue(NewickParser.is_non_terminal_subtree(data_string))
        data_string = "(a,b)c"
        self.assertTrue(NewickParser.is_non_terminal_subtree(data_string))
        data_string = "(a,c):5"
        self.assertTrue(NewickParser.is_non_terminal_subtree(data_string))
        data_string = "(a,c)c:5"
        self.assertTrue(NewickParser.is_non_terminal_subtree(data_string))

if __name__ == '__main__':
    unittest.main()
