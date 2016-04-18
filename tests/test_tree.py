# -*- coding: utf-8 -*-

from ete3 import TreeNode

from bg.edge import BGEdge
from bg.genome import BGGenome
from bg.multicolor import Multicolor
from bg.tree import BGTree

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest


class BGTreeTestCase(unittest.TestCase):
    def setUp(self):
        # commonly used values during the test cases
        v1, v2, v3, v4, v5 = "v1", "v2", "v3", "v4", "v5"
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4
        self.v5 = v5
        self.bg_v1 = BGGenome(self.v1)
        self.bg_v2 = BGGenome(self.v2)
        self.bg_v3 = BGGenome(self.v3)
        self.bg_v4 = BGGenome(self.v4)
        self.bg_v5 = BGGenome(self.v5)

    def test_edge_length(self):
        # every edge in a tree has a length
        # if no specific length, was specified on edge addition, a default value (1) is stored for this edge
        tree = BGTree("(v1:5)v2;")
        self.assertEqual(tree.get_distance(node1_name=self.v1, node2_name=self.v2), 5)
        self.assertEqual(tree.get_distance(node1_name=self.v2, node2_name=self.v1), 5)
        # edge_length lookup is available only for existing edges, thus both vertices have to be present
        # and an edge between them must exist
        with self.assertRaises(ValueError):
            tree.get_distance(node1_name=self.v1, node2_name=self.v3)
        with self.assertRaises(ValueError):
            tree.get_distance(node1_name=self.v3, node2_name=self.v4)
        with self.assertRaises(ValueError):
            tree.get_distance(node1_name=self.v3, node2_name=self.v4)

    def test_add_edge(self):
        # an edge supports an operation to add a new edge (branch) to the tree
        # if vertices of specified edge were not present in the tree, they are added automatically
        tree = BGTree("(v1:5)v2;")
        tree.multicolors_are_up_to_date = True
        tree.add_edge(node1_name=self.v1, node2_name=self.v3)
        self.assertFalse(tree.multicolors_are_up_to_date)
        self.assertEqual(len(list(tree.nodes())), 3)
        self.assertEqual(len(list(tree.edges())), 2)
        self.assertEqual(tree.get_distance(self.v1, self.v2), 5)
        self.assertEqual(tree.get_distance(self.v1, self.v3), 1)
        self.assertEqual(tree.get_distance(self.v2, self.v3), 6)
        self.assertFalse(tree.multicolors_are_up_to_date)

    def test_add_edge_explicit_edge_length(self):
        # when an edge is added, one can explicitly set its length
        tree = BGTree("(v1)v2;")
        tree.multicolors_are_up_to_date = True
        tree.add_edge(node1_name=self.v2, node2_name=self.v3, edge_length=5)
        self.assertFalse(tree.multicolors_are_up_to_date)
        self.assertEqual(len(list(tree.nodes())), 3)
        self.assertEqual(len(list(tree.edges())), 2)
        self.assertEqual(tree.get_distance(self.v1, self.v3), 6)
        self.assertEqual(tree.get_distance(self.v2, self.v3), 5)
        self.assertFalse(tree.multicolors_are_up_to_date)

    def test_has_edge_direction(self):
        tree = BGTree("((v1, v2:5)v3, v4)root;")
        self.assertTrue(tree.has_edge(self.v3, self.v1))
        self.assertFalse(tree.has_edge(self.v1, self.v3))
        self.assertTrue(tree.has_edge(self.v3, self.v2))
        self.assertFalse(tree.has_edge(self.v2, self.v3))
        self.assertTrue(tree.has_edge("root", self.v3))
        self.assertFalse(tree.has_edge(self.v3, "root"))
        self.assertTrue(tree.has_edge("root", self.v4))
        self.assertFalse(tree.has_edge(self.v4, "root"))

        self.assertFalse(tree.has_edge(self.v1, self.v2))
        self.assertFalse(tree.has_edge(self.v2, self.v1))
        self.assertFalse(tree.has_edge(self.v3, self.v4))
        self.assertFalse(tree.has_edge(self.v4, self.v3))
        self.assertFalse(tree.has_edge(self.v1, self.v4))
        self.assertFalse(tree.has_edge(self.v4, self.v1))

    def test_has_edge_no_direction(self):
        tree = BGTree("((v1, v2:5)v3, v4)root;")
        self.assertTrue(tree.has_edge(self.v3, self.v1, account_for_direction=False))
        self.assertTrue(tree.has_edge(self.v1, self.v3, account_for_direction=False))
        self.assertTrue(tree.has_edge(self.v3, self.v2, account_for_direction=False))
        self.assertTrue(tree.has_edge(self.v2, self.v3, account_for_direction=False))
        self.assertTrue(tree.has_edge("root", self.v3, account_for_direction=False))
        self.assertTrue(tree.has_edge(self.v3, "root", account_for_direction=False))
        self.assertTrue(tree.has_edge("root", self.v4, account_for_direction=False))
        self.assertTrue(tree.has_edge(self.v4, "root", account_for_direction=False))

        self.assertFalse(tree.has_edge(self.v1, self.v2, account_for_direction=False))
        self.assertFalse(tree.has_edge(self.v2, self.v1, account_for_direction=False))
        self.assertFalse(tree.has_edge(self.v3, self.v4, account_for_direction=False))
        self.assertFalse(tree.has_edge(self.v4, self.v3, account_for_direction=False))
        self.assertFalse(tree.has_edge(self.v1, self.v4, account_for_direction=False))
        self.assertFalse(tree.has_edge(self.v4, self.v1, account_for_direction=False))

    def test_has_node(self):
        # tree has a O(1) method to check if a node is present in a tree
        tree = BGTree("(v1, v2)root;")
        self.assertTrue(tree.has_node(self.v1))
        self.assertTrue(tree.has_node(self.v2))
        self.assertTrue(tree.has_node("root"))
        self.assertFalse(tree.has_node(self.v4))

    def test_append_tree_no_copy(self):
        tree1 = BGTree("(v1, v2)root;")
        tree2 = BGTree("(v4, v5)v3;")
        tree1.multicolors_are_up_to_date = True
        tree2.multicolors_are_up_to_date = True
        tree1.append(node_name=self.v1, tree=tree2)
        #####
        self.assertFalse(tree1.multicolors_are_up_to_date)
        self.assertEqual(len(list(tree1.nodes())), 6)
        self.assertEqual(len(list(tree1.edges())), 5)
        self.assertTrue(tree1.has_edge(node1_name=self.v1, node2_name=self.v3))
        #####
        self.assertTrue(tree2.multicolors_are_up_to_date)
        self.assertEqual(len(list(tree2.nodes())), 3)
        self.assertEqual(len(list(tree2.edges())), 2)
        tree1.get_node_by_name("v5").name = "new_v5"
        self.assertFalse(tree2.has_node("v5"))

    def test_append_tree_copy(self):
        tree1 = BGTree("(v1, v2)root;")
        tree2 = BGTree("(v4, v5)v3;")
        tree1.multicolors_are_up_to_date = True
        tree2.multicolors_are_up_to_date = True
        tree1.append(node_name=self.v1, tree=tree2, copy=True)
        #####
        self.assertFalse(tree1.multicolors_are_up_to_date)
        self.assertEqual(len(list(tree1.nodes())), 6)
        self.assertEqual(len(list(tree1.edges())), 5)
        self.assertTrue(tree1.has_edge(node1_name=self.v1, node2_name=self.v3))
        #####
        self.assertTrue(tree2.multicolors_are_up_to_date)
        self.assertEqual(len(list(tree2.nodes())), 3)
        self.assertEqual(len(list(tree2.edges())), 2)
        tree1.get_node_by_name("v5").name = "new_v5"
        self.assertTrue(tree2.has_node("v5"))

    def test_get_tree_consistent_multicolors(self):
        # with no account for wgd root specification is irrelevant
        tree = BGTree("(((v1, v2), v3),(v4, v5));")
        self.assertFalse(tree.multicolors_are_up_to_date)
        tree_consistent_multicolors = tree.get_tree_consistent_multicolors()
        self.assertTrue(tree.multicolors_are_up_to_date)
        self.assertIsInstance(tree_consistent_multicolors, list)
        self.assertTrue(tree_consistent_multicolors, tree.tree_consistent_multicolors)
        self.assertFalse(tree_consistent_multicolors is tree.tree_consistent_multicolors)
        for obtained_mc, stored_mc in zip(tree_consistent_multicolors, tree.tree_consistent_multicolors):
            self.assertFalse(obtained_mc is stored_mc)
        self.assertSetEqual({mc.hashable_representation for mc in tree_consistent_multicolors},
                            tree.tree_consistent_multicolors_set)
        self.assertEqual(len(tree_consistent_multicolors), 16)
        ref_tree_consistent_multicolors = [
            Multicolor(), Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5),
            Multicolor(self.bg_v1), Multicolor(self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5),
            Multicolor(self.bg_v2), Multicolor(self.bg_v1, self.bg_v3, self.bg_v4, self.bg_v5),
            Multicolor(self.bg_v3), Multicolor(self.bg_v1, self.bg_v2, self.bg_v4, self.bg_v5),
            Multicolor(self.bg_v4), Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v5),
            Multicolor(self.bg_v5), Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4),
            Multicolor(self.bg_v1, self.bg_v2), Multicolor(self.bg_v3, self.bg_v4, self.bg_v5),
            Multicolor(self.bg_v4, self.bg_v5), Multicolor(self.bg_v1, self.bg_v2, self.bg_v3),
        ]
        for multicolor in ref_tree_consistent_multicolors:
            self.assertIn(multicolor, tree_consistent_multicolors)

    def test_is_multicolor_tree_consistent(self):
        # tests if supplied multicolor complies with tree topology
        ##########################################################################################
        #
        # empty multicolor complies with any tree
        #
        ##########################################################################################
        mc = Multicolor()
        self.assertTrue(BGTree().multicolor_is_tree_consistent(mc))
        ##########################################################################################
        #
        # simple cases
        #
        ##########################################################################################
        tree = BGTree("(((v1, v2), v3),(v4, v5));")
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1)))
        ##########################################################################################
        #
        # a small v1, v2 subtree, still consistent
        #
        ##########################################################################################
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2)))
        ##########################################################################################
        #
        # bigger v1, v2, v3 subtree, still consistent
        #
        ##########################################################################################
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2, self.bg_v3)))
        ##########################################################################################
        #
        # v2, v3 is not a valid subtree (its compliment is two subtrees, instead of one)
        #
        ##########################################################################################
        self.assertFalse(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v2, self.bg_v3)))
        ##########################################################################################
        #
        # if some genomes in multicolor are not present in tree, then multicolor will not be consistent with the tree
        #
        ##########################################################################################
        self.assertFalse(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, BGGenome("v6"))))
        ##########################################################################################
        #
        # other cases for a non wgd tree
        #
        ##########################################################################################
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v5)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2, self.bg_v4, self.bg_v5)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v3, self.bg_v4, self.bg_v5)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v5, self.bg_v4)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v3, self.bg_v4, self.bg_v5)))
        self.assertFalse(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v3, self.bg_v5)))

    def test_is_multicolor_tree_consistent_non_binary_tree(self):
        tree = BGTree("(v1, v2, v3);")
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v2)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v3)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2, self.bg_v3)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v3)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v3, self.bg_v2)))

    def test_is_bgedge_tree_consistent(self):
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
        self.assertTrue(BGTree("(v1, v2);").bgedge_is_tree_consistent(bgedge))
        ##########################################################################################
        #
        # simple cases
        #
        ##########################################################################################
        tree = BGTree("(((v1, v2), v3),(v4, v5));")
        bgedge.multicolor = Multicolor(self.bg_v1)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        ##########################################################################################
        #
        # a small v1, v2 subtree, still consistent
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        ##########################################################################################
        #
        # bigger v1, v2, v3 subtree, still consistent
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v3)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        ##########################################################################################
        #
        # v2, v3 is not a valid subtree (its compliment is two subtrees, instead of one)
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v2, self.bg_v3)
        self.assertFalse(tree.bgedge_is_tree_consistent(bgedge))
        ##########################################################################################
        #
        # if some genomes in multicolor are not present in tree, then multicolor will not be consistent with the tree
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v1, BGGenome("v6"))
        self.assertFalse(tree.bgedge_is_tree_consistent(bgedge))
        ##########################################################################################
        #
        # other cases for a non wgd tree
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v5)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v4, self.bg_v5)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v3, self.bg_v4, self.bg_v5)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v5, self.bg_v4)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v3, self.bg_v4, self.bg_v5)
        self.assertTrue(tree.bgedge_is_tree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v3, self.bg_v5)
        self.assertFalse(tree.bgedge_is_tree_consistent(bgedge))

    def test_get_vtree_consistent_multicolors(self):
        tree = BGTree("(((v1, v2), v3),(v4, v5));")
        self.assertFalse(tree.multicolors_are_up_to_date)
        vtree_consistent_multicolors = tree.get_vtree_consistent_multicolors()
        self.assertTrue(tree.multicolors_are_up_to_date)
        self.assertIsInstance(vtree_consistent_multicolors, list)
        self.assertTrue(vtree_consistent_multicolors, tree.vtree_consistent_multicolors)
        self.assertFalse(vtree_consistent_multicolors is tree.vtree_consistent_multicolors)
        for obtained_mc, stored_mc in zip(vtree_consistent_multicolors, tree.vtree_consistent_multicolors):
            self.assertFalse(obtained_mc is stored_mc)
        self.assertSetEqual({mc.hashable_representation for mc in vtree_consistent_multicolors},
                            tree.vtree_consistent_multicolors_set)
        self.assertEqual(len(vtree_consistent_multicolors), 10)
        ref_vtree_consistent_multicolors = [
            Multicolor(), Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5),
            Multicolor(self.bg_v1),
            Multicolor(self.bg_v2),
            Multicolor(self.bg_v3),
            Multicolor(self.bg_v4),
            Multicolor(self.bg_v5),
            Multicolor(self.bg_v1, self.bg_v2),
            Multicolor(self.bg_v4, self.bg_v5), Multicolor(self.bg_v1, self.bg_v2, self.bg_v3),
        ]
        for multicolor in ref_vtree_consistent_multicolors:
            self.assertIn(multicolor, vtree_consistent_multicolors)

    def test_is_multicolor_vtree_consistent(self):
        mc = Multicolor()
        self.assertTrue(BGTree().multicolor_is_vtree_consistent(mc))

        tree = BGTree("(((v1, v2), v3), (v4, v5));")
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v4, self.bg_v5)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2, self.bg_v3)))
        self.assertTrue(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5)))
        self.assertFalse(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v2, self.bg_v3)))
        self.assertFalse(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v1, BGGenome("v6"))))
        self.assertFalse(tree.multicolor_is_tree_consistent(Multicolor(self.bg_v3, self.bg_v5)))

    def test_is_multicolor_vtree_consistent_non_binary_tree(self):
        tree = BGTree("(v1, v2, v3);")
        self.assertTrue(tree.multicolor_is_vtree_consistent(Multicolor(self.bg_v1)))
        self.assertTrue(tree.multicolor_is_vtree_consistent(Multicolor(self.bg_v2)))
        self.assertTrue(tree.multicolor_is_vtree_consistent(Multicolor(self.bg_v3)))
        self.assertTrue(tree.multicolor_is_vtree_consistent(Multicolor(self.bg_v1, self.bg_v2, self.bg_v3)))
        self.assertFalse(tree.multicolor_is_vtree_consistent(Multicolor(self.bg_v1, self.bg_v2)))
        self.assertFalse(tree.multicolor_is_vtree_consistent(Multicolor(self.bg_v1, self.bg_v3)))
        self.assertFalse(tree.multicolor_is_vtree_consistent(Multicolor(self.bg_v3, self.bg_v2)))

    def test_is_bgedge_vtree_consistent(self):
        v1, v2 = "v1", "v2"
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=Multicolor())
        ##########################################################################################
        #
        # bgedge with an empty multicolor complies with any tree
        #
        ##########################################################################################
        mc = Multicolor()
        bgedge.multicolor = mc
        self.assertTrue(BGTree("(v1, v2);").bgedge_is_vtree_consistent(bgedge))
        ##########################################################################################
        #
        # simple cases
        #
        ##########################################################################################
        tree = BGTree("(((v1, v2), v3),(v4, v5));")
        bgedge.multicolor = Multicolor(self.bg_v1)
        self.assertTrue(tree.bgedge_is_vtree_consistent(bgedge))
        ##########################################################################################
        #
        # a small v1, v2 subtree, still consistent
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2)
        self.assertTrue(tree.bgedge_is_vtree_consistent(bgedge))
        ##########################################################################################
        #
        # bigger v1, v2, v3 subtree, still consistent
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v3)
        self.assertTrue(tree.bgedge_is_vtree_consistent(bgedge))
        ##########################################################################################
        #
        # v2, v3 is not a valid subtree (its compliment is two subtrees, instead of one)
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v2, self.bg_v3)
        self.assertFalse(tree.bgedge_is_vtree_consistent(bgedge))
        ##########################################################################################
        #
        # if some genomes in multicolor are not present in tree, then multicolor will not be consistent with the tree
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v1, BGGenome("v6"))
        self.assertFalse(tree.bgedge_is_vtree_consistent(bgedge))
        ##########################################################################################
        #
        # other cases for a non wgd tree
        #
        ##########################################################################################
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4)
        self.assertFalse(tree.bgedge_is_vtree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v5)
        self.assertFalse(tree.bgedge_is_vtree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v4, self.bg_v5)
        self.assertFalse(tree.bgedge_is_vtree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v3, self.bg_v4, self.bg_v5)
        self.assertFalse(tree.bgedge_is_vtree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5)
        self.assertFalse(tree.bgedge_is_vtree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v1, self.bg_v2, self.bg_v3, self.bg_v4, self.bg_v5)
        self.assertTrue(tree.bgedge_is_vtree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v5, self.bg_v4)
        self.assertTrue(tree.bgedge_is_vtree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v3, self.bg_v4, self.bg_v5)
        self.assertFalse(tree.bgedge_is_vtree_consistent(bgedge))
        bgedge.multicolor = Multicolor(self.bg_v3, self.bg_v5)
        self.assertFalse(tree.bgedge_is_vtree_consistent(bgedge))

    def test_get_tree_consistent_multicolors_with_non_default_leaf_wrapper(self):
        tree = BGTree("(v1, v2)root;", leaf_wrapper=lambda name: name)
        tree_consistent_multicolors = tree.get_tree_consistent_multicolors()
        ref_multicolors = [Multicolor(self.v1), Multicolor(self.v2), Multicolor(), Multicolor(self.v1, self.v2)]
        self.assertEqual(len(tree_consistent_multicolors), 4)
        for mc in tree_consistent_multicolors:
            self.assertIn(mc, ref_multicolors)

    def test_edges_empty_tree(self):
        tree = BGTree()
        self.assertEqual(len(list(tree.edges())), 0)

    def test_edges_binary_tree(self):
        tree = BGTree(newick="((a, (b, c)), (d, (e, (f, g))));", leaf_wrapper=BGGenome)
        edges = list(tree.edges())
        self.assertEqual(len(edges), 12)
        for edge in edges:
            self.assertIsInstance(edge, tuple)
            self.assertEqual(len(edge), 2)
            self.assertTrue(isinstance(edge[0], BGGenome) or isinstance(edge[0], TreeNode))
            self.assertTrue(isinstance(edge[1], BGGenome) or isinstance(edge[1], TreeNode))
        leaf_edges = [edge for edge in edges if isinstance(edge[0], BGGenome) or isinstance(edge[1], BGGenome)]
        self.assertEqual(len(leaf_edges), 7)

    def test_edges_non_binary_tree(self):
        tree = BGTree(newick="((a, b, c), (d, e, (f, g, e)));", leaf_wrapper=BGGenome)
        edges = list(tree.edges())
        self.assertEqual(len(edges), 11)
        for edge in edges:
            self.assertIsInstance(edge, tuple)
            self.assertEqual(len(edge), 2)
            self.assertTrue(isinstance(edge[0], BGGenome) or isinstance(edge[0], TreeNode))
            self.assertTrue(isinstance(edge[1], BGGenome) or isinstance(edge[1], TreeNode))
        leaf_edges = [edge for edge in edges if isinstance(edge[0], BGGenome) or isinstance(edge[1], BGGenome)]
        self.assertEqual(len(leaf_edges), 8)

if __name__ == '__main__':
    unittest.main()
