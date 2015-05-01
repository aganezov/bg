# -*- coding: utf-8 -*-
from unittest.mock import Mock
from bg import Multicolor, BGEdge
from bg.genome import BGGenome
from bg.tree import BGTree, NewickReader, DEFAULT_EDGE_LENGTH

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest


class BGTreeTestCase(unittest.TestCase):
    def setUp(self):
        # commonly used values during the test cases
        v1, v2, v3, v4, v5 = BGGenome("v1"), BGGenome("v2"), BGGenome("v3"), BGGenome("v4"), BGGenome("v5")
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4
        self.v5 = v5

    def test_empty_tree_initialization(self):
        # empty tree shall be initialized with no nodes and branches in it
        tree = BGTree()
        self.assertIsNone(tree.root)
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 0)
        self.assertEqual(len(list(tree.edges())), 0)
        self.assertListEqual(tree.consistent_multicolors, [Multicolor()])
        self.assertSetEqual(tree.consistent_multicolors_set, {Multicolor().hashable_representation})
        self.assertFalse(tree.account_for_wgd)
        self.assertTrue(tree.multicolors_are_up_to_date)

    def test_add_genome(self):
        # tree support additional of genomes on their own, without edges
        # this is the case for a tree with a single node
        tree = BGTree()
        tree.add_node(BGGenome("genome"))
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 1)
        self.assertEqual(len(list(tree.edges())), 0)
        self.assertFalse(tree.multicolors_are_up_to_date)

    def test_edge_length(self):
        # every edge in a tree has a length
        # if no specific length, was specified on edge addition, a default value (1) is stored for this edge
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, edge_length=5)
        self.assertEqual(tree.edge_length(vertex1=self.v1, vertex2=self.v2), 5)
        self.assertEqual(tree.edge_length(vertex1=self.v2, vertex2=self.v1), 5)
        # edge_length lookup is available only for existing edges, thus both vertices have to be present
        # and an edge between them must exist
        with self.assertRaises(ValueError):
            tree.edge_length(vertex1=self.v1, vertex2=self.v3)
        with self.assertRaises(ValueError):
            tree.edge_length(vertex1=self.v3, vertex2=self.v4)
        with self.assertRaises(ValueError):
            tree.edge_length(vertex1=self.v3, vertex2=self.v4)

    def test_edge_wgd_information(self):
        # every edge in a tree has a number of whole genome duplication (wgd) events assigned to it
        # if no specific count of wgd events was assigned to the edge, a default value (0) is stored for this edge
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, wgd_events=5)
        tree.add_edge(vertex1=self.v1, vertex2=self.v3)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v2, vertex2=self.v1), 5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v3), 0)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v3, vertex2=self.v1), 0)
        # edge_wgd_count lookup is available only for existing edges, thus both vertices have to be present
        # and an edge between them must exist
        with self.assertRaises(ValueError):
            tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v4)
        with self.assertRaises(ValueError):
            tree.edge_wgd_count(vertex1=self.v3, vertex2=self.v4)

    def test_add_edge(self):
        # an edge supports an operation to add a new edge (branch) to the tree
        # if vertices of specified edge were not present in the tree, they are added automatically
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 2)
        self.assertEqual(len(list(tree.edges())), 1)
        self.assertEqual(tree.edge_length(self.v1, self.v2), 1)
        self.assertFalse(tree.multicolors_are_up_to_date)

    def test_add_edge_explicit_edge_length(self):
        # when an edge is added, one can explicitly set its length
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, edge_length=5)
        self.assertTrue(tree.is_valid_tree)
        self.assertEqual(len(list(tree.nodes())), 2)
        self.assertEqual(len(list(tree.edges())), 1)
        self.assertEqual(tree.edge_length(self.v1, self.v2), 5)
        self.assertFalse(tree.multicolors_are_up_to_date)

    def test_add_edge_explicit_wgd(self):
        # when an edge is added, one can explicitly set the number of whole genome duplication events associated with it
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2, wgd_events=5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 5)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v2, vertex2=self.v1), 5)
        self.assertFalse(tree.multicolors_are_up_to_date)

    def test_has_edge(self):
        # tree has a O(1) method to check, if an edge exists between two given vertices
        # if vertices are not present in the graph, no exception is raised
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
        # tree has a O(1) method to check if a node is present in a tree
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        tree.add_node(self.v3)
        self.assertTrue(tree.has_node(self.v1))
        self.assertTrue(tree.has_node(self.v2))
        self.assertTrue(tree.has_node(self.v3))
        self.assertFalse(tree.has_node(self.v4))

    def test_assign_root(self):
        # a tree has a special pointer to a node, that represents a root of the tree
        # a root can be set to None, though, which shall not in a right-full mind be present in a tree
        tree = BGTree()
        self.assertIsNone(tree.root)
        with self.assertRaises(ValueError):
            tree.root = self.v1
        tree.add_node(self.v1)
        tree.root = self.v1
        self.assertEqual(tree.root, self.v1)
        tree.root = None
        self.assertIsNone(tree.root)
        self.assertFalse(tree.multicolors_are_up_to_date)

    def test_append_tree(self):
        # two trees can be combined together
        # a union of vertices and edges is obtained in it
        tree1 = BGTree()
        tree2 = BGTree()
        tree1.add_edge(vertex1=self.v1, vertex2=self.v2)
        tree2.add_edge(vertex1=self.v2, vertex2=self.v3)
        self.assertTrue(tree1.is_valid_tree)
        self.assertTrue(tree2.is_valid_tree)
        tree1.multicolors_are_up_to_date = True
        tree2.multicolors_are_up_to_date = True
        tree1.append(tree=tree2)
        #####
        self.assertFalse(tree1.multicolors_are_up_to_date)
        self.assertTrue(tree1.is_valid_tree)
        self.assertEqual(len(list(tree1.nodes())), 3)
        self.assertEqual(len(list(tree1.edges())), 2)
        self.assertTrue(tree1.has_edge(vertex1=self.v3, vertex2=self.v2))
        self.assertTrue(tree1.has_edge(vertex1=self.v1, vertex2=self.v2))
        #####
        self.assertTrue(tree2.multicolors_are_up_to_date)
        self.assertTrue(tree2.is_valid_tree)
        self.assertEqual(len(list(tree2.nodes())), 2)
        self.assertEqual(len(list(tree2.edges())), 1)

    def test_set_wgd_count_correct(self):
        # a wgd events count can be set for a specific edge explicitly
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        tree.multicolors_are_up_to_date = True
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 0)
        tree.set_wgd_count(vertex1=self.v1, vertex2=self.v2, wgd_count=2)
        self.assertFalse(tree.multicolors_are_up_to_date)
        tree.multicolors_are_up_to_date = True
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 2)
        tree.set_wgd_count(vertex1=self.v2, vertex2=self.v1, wgd_count=3)
        self.assertEqual(tree.edge_wgd_count(vertex1=self.v1, vertex2=self.v2), 3)
        self.assertFalse(tree.multicolors_are_up_to_date)

    def test_set_wgd_count_incorrect(self):
        # only for existing edges such setup if possible
        tree = BGTree()
        tree.multicolors_are_up_to_date = True
        with self.assertRaises(ValueError):
            self.assertEqual(tree.set_wgd_count(vertex1=self.v1, vertex2=self.v2, wgd_count=2), 2)
        # only positive integers are allowed as values for whole genome duplication count
        self.assertTrue(tree.multicolors_are_up_to_date)
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        tree.multicolors_are_up_to_date = True
        incorrect_counts = [0.5, "a", (1,), [1]]
        for incorrect_count in incorrect_counts:
            with self.assertRaises(ValueError):
                tree.set_wgd_count(vertex1=self.v1, vertex2=self.v2, wgd_count=incorrect_count)
            self.assertTrue(tree.multicolors_are_up_to_date)

    def test_set_edge_length(self):
        # a length of a specific edge can be set explicitly
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

    def test_get_tree_consistent_multicolors_unrooted_no_wgd_empty(self):
        # in unrooted tree multicolors are tree consistent, if they represent a perfect split of a tree
        # resulting from deletion of a single edge
        # in this case whole genome duplication are not taken into account, as wgd is a directed event
        # and without a root no direction can be chosen
        tree = BGTree()
        tree.account_for_wgd = True
        tree_consistent_multicolors = tree.get_tree_consistent_multicolors(rooted=False, account_for_wgd=False)
        self.assertFalse(tree.account_for_wgd)
        self.assertTrue(tree.multicolors_are_up_to_date)
        self.assertIsInstance(tree_consistent_multicolors, list)
        self.assertListEqual(tree_consistent_multicolors, tree.consistent_multicolors)
        self.assertFalse(tree_consistent_multicolors is tree.consistent_multicolors)
        for obtained_mc, stored_mc in zip(tree_consistent_multicolors, tree.consistent_multicolors):
            self.assertFalse(obtained_mc is stored_mc)
        self.assertSetEqual({mc.hashable_representation for mc in tree_consistent_multicolors},
                            tree.consistent_multicolors_set)
        self.assertEqual(len(tree_consistent_multicolors), 1)
        self.assertIn(Multicolor(), tree_consistent_multicolors)

    def test_get_tree_consistent_multicolors_unrooted_no_wgd_correct(self):
        # if `rooted` argument is set to `False`, then regardless of `tree.root` value outcome shall be the same
        tree = NewickReader.from_string(data_string="(((v1, v2), v3),(v4, v5));")
        for root in [self.v1, self.v2, self.v3, self.v4, self.v5, "1", "2", "3", "4", None]:
            tree.root = root
            self.assertFalse(tree.multicolors_are_up_to_date)
            tree_consistent_multicolors = tree.get_tree_consistent_multicolors(rooted=False, account_for_wgd=False)
            self.assertTrue(tree.multicolors_are_up_to_date)
            self.assertIsInstance(tree_consistent_multicolors, list)
            self.assertListEqual(tree_consistent_multicolors, tree.consistent_multicolors)
            self.assertFalse(tree_consistent_multicolors is tree.consistent_multicolors)
            for obtained_mc, stored_mc in zip(tree_consistent_multicolors, tree.consistent_multicolors):
                self.assertFalse(obtained_mc is stored_mc)
            self.assertSetEqual({mc.hashable_representation for mc in tree_consistent_multicolors},
                                tree.consistent_multicolors_set)
            self.assertEqual(len(tree_consistent_multicolors), 16)
            ref_tree_consistent_multicolors = [
                Multicolor(), Multicolor(self.v1, self.v2, self.v3, self.v4, self.v5),
                Multicolor(self.v1), Multicolor(self.v2, self.v3, self.v4, self.v5),
                Multicolor(self.v2), Multicolor(self.v1, self.v3, self.v4, self.v5),
                Multicolor(self.v3), Multicolor(self.v1, self.v2, self.v4, self.v5),
                Multicolor(self.v4), Multicolor(self.v1, self.v2, self.v3, self.v5),
                Multicolor(self.v5), Multicolor(self.v1, self.v2, self.v3, self.v4),
                Multicolor(self.v1, self.v2), Multicolor(self.v3, self.v4, self.v5),
                Multicolor(self.v4, self.v5), Multicolor(self.v1, self.v2, self.v3),
            ]
            for multicolor in ref_tree_consistent_multicolors:
                self.assertIn(multicolor, tree_consistent_multicolors)

    def test_get_tree_consistent_multicolors_rooted_no_wgd_correct(self):
        # with no account for wgd root specification is irrelevant
        tree = NewickReader.from_string(data_string="(((v1, v2), v3),(v4, v5));")
        for root in [self.v1, self.v2, self.v3, self.v4, self.v4, "1", "2", "3"]:
            tree.root = root
            self.assertFalse(tree.multicolors_are_up_to_date)
            tree_consistent_multicolors = tree.get_tree_consistent_multicolors(rooted=True, account_for_wgd=False)
            self.assertTrue(tree.multicolors_are_up_to_date)
            self.assertIsInstance(tree_consistent_multicolors, list)
            self.assertTrue(tree_consistent_multicolors, tree.consistent_multicolors)
            self.assertFalse(tree_consistent_multicolors is tree.consistent_multicolors)
            for obtained_mc, stored_mc in zip(tree_consistent_multicolors, tree.consistent_multicolors):
                self.assertFalse(obtained_mc is stored_mc)
            self.assertSetEqual({mc.hashable_representation for mc in tree_consistent_multicolors},
                                tree.consistent_multicolors_set)
            self.assertEqual(len(tree_consistent_multicolors), 16)
            ref_tree_consistent_multicolors = [
                Multicolor(), Multicolor(self.v1, self.v2, self.v3, self.v4, self.v5),
                Multicolor(self.v1), Multicolor(self.v2, self.v3, self.v4, self.v5),
                Multicolor(self.v2), Multicolor(self.v1, self.v3, self.v4, self.v5),
                Multicolor(self.v3), Multicolor(self.v1, self.v2, self.v4, self.v5),
                Multicolor(self.v4), Multicolor(self.v1, self.v2, self.v3, self.v5),
                Multicolor(self.v5), Multicolor(self.v1, self.v2, self.v3, self.v4),
                Multicolor(self.v1, self.v2), Multicolor(self.v3, self.v4, self.v5),
                Multicolor(self.v4, self.v5), Multicolor(self.v1, self.v2, self.v3),
            ]
            for multicolor in ref_tree_consistent_multicolors:
                self.assertIn(multicolor, tree_consistent_multicolors)

    def test_get_tree_consistent_multicolors_with_wgd_incorrect(self):
        # if `account_for_wgd` option is set to `True`, `rooted` argument must be set to `True` as well
        tree = BGTree()
        tree.multicolors_are_up_to_date = False
        with self.assertRaises(ValueError):
            tree.get_tree_consistent_multicolors(rooted=False, account_for_wgd=True)
        self.assertFalse(tree.multicolors_are_up_to_date)
        # root of the tree must be not None (can happen if tree is built manually)
        tree = BGTree()
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        with self.assertRaises(ValueError):
            tree.get_tree_consistent_multicolors(rooted=False, account_for_wgd=True)
        self.assertFalse(tree.multicolors_are_up_to_date)

    def test_get_tree_consistent_multicolors_with_wgd_correct_non_leaf_root(self):
        # if a root is specified, each wgd even shall duplicate the number of respected genome ends
        tree = NewickReader.from_string(data_string="(((v1, v2), v3),(v4, v5));")
        tree.set_wgd_count(vertex1=self.v1, vertex2="3", wgd_count=1)
        tree.set_wgd_count(vertex1="3", vertex2="2", wgd_count=2)
        tree.root = "1"
        self.assertFalse(tree.multicolors_are_up_to_date)
        tree_consistent_multicolors = tree.get_tree_consistent_multicolors(rooted=True, account_for_wgd=True)
        self.assertTrue(tree.multicolors_are_up_to_date)
        self.assertIsInstance(tree_consistent_multicolors, list)
        self.assertListEqual(tree_consistent_multicolors, tree.consistent_multicolors)
        self.assertFalse(tree_consistent_multicolors is tree.consistent_multicolors)
        for obtained_mc, stored_mc in zip(tree_consistent_multicolors, tree.consistent_multicolors):
            self.assertFalse(obtained_mc is stored_mc)
        self.assertSetEqual({mc.hashable_representation for mc in tree_consistent_multicolors},
                            tree.consistent_multicolors_set)
        self.assertEqual(len(tree_consistent_multicolors), 22)
        overall_multicolor = Multicolor(self.v1) * 8 + Multicolor(self.v2) * 4 + Multicolor(self.v3, self.v4, self.v5)
        ref_tree_consistent_multicolor = [
            Multicolor(), overall_multicolor,
            Multicolor(self.v1), overall_multicolor - Multicolor(self.v1),
            Multicolor(self.v2), overall_multicolor - Multicolor(self.v2),
            Multicolor(self.v3), overall_multicolor - Multicolor(self.v3),
            Multicolor(self.v4), overall_multicolor - Multicolor(self.v4),
            Multicolor(self.v5), overall_multicolor - Multicolor(self.v5),
            Multicolor(self.v1) * 2, overall_multicolor - Multicolor(self.v1) * 2,
            Multicolor(self.v1) * 2 + Multicolor(self.v2), overall_multicolor - Multicolor(self.v1) * 2 - Multicolor(self.v2),
            Multicolor(self.v1) * 4 + Multicolor(self.v2) * 2, overall_multicolor - Multicolor(self.v1) * 4 - Multicolor(self.v2) * 2,
            Multicolor(self.v1) * 8 + Multicolor(self.v2) * 4, overall_multicolor - Multicolor(self.v1) * 8 - Multicolor(self.v2) * 4,
            Multicolor(self.v1) * 8 + Multicolor(self.v2) * 4 + Multicolor(self.v3), Multicolor(self.v4, self.v5),
        ]
        for multicolor in tree_consistent_multicolors:
            self.assertIn(multicolor, ref_tree_consistent_multicolor)

    def test_get_tree_consistent_multicolors_no_wgd_correct_specified_by_argument(self):
        # with rooted tree, if account_for_wgd is set to False, result shall be the same, if it was not rooted
        tree = NewickReader.from_string(data_string="(((v1, v2), v3),(v4, v5));")
        tree.set_wgd_count(vertex1=self.v1, vertex2="3", wgd_count=1)
        tree.set_wgd_count(vertex1="3", vertex2="2", wgd_count=2)
        tree.root = "1"
        self.assertFalse(tree.multicolors_are_up_to_date)
        tree_consistent_multicolors = tree.get_tree_consistent_multicolors(rooted=True, account_for_wgd=False)
        self.assertTrue(tree.multicolors_are_up_to_date)
        self.assertIsInstance(tree_consistent_multicolors, list)
        self.assertListEqual(tree_consistent_multicolors, tree.consistent_multicolors)
        self.assertFalse(tree_consistent_multicolors is tree.consistent_multicolors)
        for obtained_mc, stored_mc in zip(tree_consistent_multicolors, tree.consistent_multicolors):
            self.assertFalse(obtained_mc is stored_mc)
        self.assertEqual(len(tree_consistent_multicolors), 16)
        ref_tree_consistent_multicolors = [
                Multicolor(), Multicolor(self.v1, self.v2, self.v3, self.v4, self.v5),
                Multicolor(self.v1), Multicolor(self.v2, self.v3, self.v4, self.v5),
                Multicolor(self.v2), Multicolor(self.v1, self.v3, self.v4, self.v5),
                Multicolor(self.v3), Multicolor(self.v1, self.v2, self.v4, self.v5),
                Multicolor(self.v4), Multicolor(self.v1, self.v2, self.v3, self.v5),
                Multicolor(self.v5), Multicolor(self.v1, self.v2, self.v3, self.v4),
                Multicolor(self.v1, self.v2), Multicolor(self.v3, self.v4, self.v5),
                Multicolor(self.v4, self.v5), Multicolor(self.v1, self.v2, self.v3),
            ]
        for multicolor in tree_consistent_multicolors:
            self.assertIn(multicolor, ref_tree_consistent_multicolors)

    def test_get_tree_consistent_multicolors_with_wgd_correct_leaf_root(self):
        # when a root is set to a leaf color it is a specific case, as the root branch shall not account
        # for tree consistent multicolor on its own, but rather provide an artificial outgoing branch
        # corresponding to the previous-to-the-tree events and overall multicolor
        tree = NewickReader.from_string(data_string="(((v1, v2), v3),(v4, v5));")
        tree.set_wgd_count(vertex1=self.v1, vertex2="3", wgd_count=1)
        tree.set_wgd_count(vertex1="3", vertex2="2", wgd_count=2)
        tree.root = self.v1
        self.assertFalse(tree.multicolors_are_up_to_date)
        tree_consistent_multicolors = tree.get_tree_consistent_multicolors(rooted=True, account_for_wgd=True)
        self.assertTrue(tree.multicolors_are_up_to_date)
        self.assertIsInstance(tree_consistent_multicolors, list)
        self.assertListEqual(tree_consistent_multicolors, tree.consistent_multicolors)
        self.assertFalse(tree_consistent_multicolors is tree.consistent_multicolors)
        for obtained_mc, stored_mc in zip(tree_consistent_multicolors, tree.consistent_multicolors):
            self.assertFalse(obtained_mc is stored_mc)
        self.assertSetEqual({mc.hashable_representation for mc in tree_consistent_multicolors},
                            tree.consistent_multicolors_set)
        self.assertEqual(len(tree_consistent_multicolors), 21)
        overall_multicolor = Multicolor(self.v1) + Multicolor(self.v2) * 2 + Multicolor(self.v4, self.v5, self.v3) * 8
        ref_tree_consistent_multicolor = [
            Multicolor(), overall_multicolor,
            overall_multicolor - Multicolor(self.v1),
            Multicolor(self.v2), overall_multicolor - Multicolor(self.v2),
            Multicolor(self.v3), overall_multicolor - Multicolor(self.v3),
            Multicolor(self.v4), overall_multicolor - Multicolor(self.v4),
            Multicolor(self.v5), overall_multicolor - Multicolor(self.v5),
            Multicolor(self.v4, self.v5), overall_multicolor - Multicolor(self.v4, self.v5),
            Multicolor(self.v4, self.v5, self.v3), overall_multicolor - Multicolor(self.v4, self.v5, self.v3),
            Multicolor(self.v4, self.v5, self.v3) * 2, overall_multicolor - Multicolor(self.v4, self.v5, self.v3) * 2,
            Multicolor(self.v4, self.v5, self.v3) * 4, overall_multicolor - Multicolor(self.v4, self.v5, self.v3) * 4,
            Multicolor(self.v4, self.v5, self.v3) * 4 + Multicolor(self.v2), overall_multicolor - Multicolor(self.v4, self.v5, self.v3) * 4 - Multicolor(self.v2),
        ]
        for multicolor in tree_consistent_multicolors:
            self.assertIn(multicolor, ref_tree_consistent_multicolor)

    def test_consistent_multicolor_transparent_update_with_change_occurring(self):
        tree = BGTree()
        tcm1 = tree.consistent_multicolors
        self.assertListEqual(tcm1, [Multicolor()])
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        tcm2 = tree.consistent_multicolors
        self.assertEqual(len(tcm2), 4)
        for mc in tcm2:
            self.assertIn(mc, [Multicolor(), Multicolor(self.v1), Multicolor(self.v2), Multicolor(self.v1, self.v2)])

    def test_consistent_multicolors_set_transparent_update_with_change_occurring(self):
        tree = BGTree()
        tcm1 = tree.consistent_multicolors_set
        self.assertSetEqual(tcm1, {Multicolor().hashable_representation})
        tree.add_edge(vertex1=self.v1, vertex2=self.v2)
        tcm2 = tree.consistent_multicolors_set
        self.assertEqual(len(tcm2), 4)
        ref = {mc.hashable_representation for mc in [Multicolor(), Multicolor(self.v1), Multicolor(self.v2), Multicolor(self.v1, self.v2)]}
        for mc in tcm2:
            self.assertIn(mc, ref)

    def test_is_multicolor_consistent(self):
        # tests if supplied multicolor complies with tree topology
        ##########################################################################################
        #
        # empty multicolor complies with any tree
        #
        ##########################################################################################
        mc = Multicolor()
        self.assertTrue(BGTree().is_multicolor_consistent(mc))
        ##########################################################################################
        #
        # simple cases
        #
        ##########################################################################################
        tree = NewickReader.from_string("(((v1, v2), v3),(v4, v5));")
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1)))
        ##########################################################################################
        #
        # a small v1, v2 subtree, still consistent
        #
        ##########################################################################################
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1, self.v2)))
        ##########################################################################################
        #
        # bigger v1, v2, v3 subtree, still consistent
        #
        ##########################################################################################
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1, self.v2, self.v3)))
        ##########################################################################################
        #
        # v2, v3 is not a valid subtree (its compliment is two subtrees, instead of one)
        #
        ##########################################################################################
        self.assertFalse(tree.is_multicolor_consistent(Multicolor(self.v2, self.v3)))
        ##########################################################################################
        #
        # if some genomes in multicolor are not present in tree, then multicolor will not be consistent with the tree
        #
        ##########################################################################################
        self.assertFalse(tree.is_multicolor_consistent(Multicolor(self.v1, BGGenome("v6"))))
        ##########################################################################################
        #
        # other cases for a non wgd tree
        #
        ##########################################################################################
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1, self.v2, self.v3, self.v4)))
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1, self.v2, self.v3, self.v5)))
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1, self.v2, self.v4, self.v5)))
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1, self.v3, self.v4, self.v5)))
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v2, self.v3, self.v4, self.v5)))
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1, self.v2, self.v3, self.v4, self.v5)))
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v5, self.v4)))
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v3, self.v4, self.v5)))
        self.assertFalse(tree.is_multicolor_consistent(Multicolor(self.v3, self.v5)))
        ##########################################################################################
        #
        # if we have account for wgd, v1, v1 san become a valid subtree
        #
        ##########################################################################################
        tree.set_wgd_count(vertex1=self.v1, vertex2="3", wgd_count=1)
        tree.root = "1"
        tree.account_for_wgd = True
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1)))
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1, self.v1)))
        self.assertFalse(tree.is_multicolor_consistent(Multicolor(self.v1, self.v2)))
        self.assertTrue(tree.is_multicolor_consistent(Multicolor(self.v1, self.v1, self.v2)))

    def test_is_bgedge_consistent(self):
        # tests if supplied bgedge has a multicolor that is consistent with tree topology
        v1, v2 = "v1", "v2"
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=Multicolor())
        ##########################################################################################
        #
        # bgedge with an empty multicolor complies with any tree
        #
        ##########################################################################################
        mc = Multicolor()
        bgedge.multicolor = mc
        self.assertTrue(BGTree().is_bgedge_consistent(bgedge))
        ##########################################################################################
        #
        # simple cases
        #
        ##########################################################################################
        tree = NewickReader.from_string("(((v1, v2), v3),(v4, v5));")
        bgedge.multicolor = Multicolor(self.v1)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        ##########################################################################################
        #
        # a small v1, v2 subtree, still consistent
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.v1, self.v2)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        ##########################################################################################
        #
        # bigger v1, v2, v3 subtree, still consistent
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.v1, self.v2, self.v3)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        ##########################################################################################
        #
        # v2, v3 is not a valid subtree (its compliment is two subtrees, instead of one)
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.v2, self.v3)
        self.assertFalse(tree.is_bgedge_consistent(bgedge))
        ##########################################################################################
        #
        # if some genomes in multicolor are not present in tree, then multicolor will not be consistent with the tree
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.v1, BGGenome("v6"))
        self.assertFalse(tree.is_bgedge_consistent(bgedge))
        ##########################################################################################
        #
        # other cases for a non wgd tree
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.v1, self.v2, self.v3, self.v4)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v1, self.v2, self.v3, self.v5)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v1, self.v2, self.v4, self.v5)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v1, self.v3, self.v4, self.v5)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v2, self.v3, self.v4, self.v5)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v1, self.v2, self.v3, self.v4, self.v5)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v5, self.v4)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v3, self.v4, self.v5)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v3, self.v5)
        self.assertFalse(tree.is_bgedge_consistent(bgedge))
        ##########################################################################################
        #
        # if we have account for wgd, v1, v1 san become a valid subtree
        #
        ##########################################################################################
        tree.set_wgd_count(vertex1=self.v1, vertex2="3", wgd_count=1)
        tree.root = "1"
        tree.account_for_wgd = True
        bgedge.multicolor = Multicolor(self.v1)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v1, self.v1)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v1, self.v2)
        self.assertFalse(tree.is_bgedge_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.v1, self.v1, self.v2)
        self.assertTrue(tree.is_bgedge_consistent(bgedge))


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
        # edge length has to be int/double and nothing else
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
        # some incorrect versions of our newick format, where empty nodes are forbidden
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
        # newick reader can determine is supplied subtree is actually a terminal node
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
        # every root has a tree in a newick format, and it will be assigned to the tree.root pointer
        # this root node name is generated (ass well as other non explicit nodes) on the fly
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
