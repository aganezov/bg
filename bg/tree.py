# -*- coding: utf-8 -*-
from collections import deque
from copy import deepcopy

from ete3 import Tree

from bg.genome import BGGenome
from bg.multicolor import Multicolor

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

# defines a default edge length in phylogenetic tree
DEFAULT_EDGE_LENGTH = 1


class BGTree(object):
    """ Class that is designed to store information about phylogenetic information and relations between multiple genomes

    Class utilizes a ete3.Tree object as an internal storage
    This tree can store information about:
        * edge lengths
        * tree topology
    """

    # class defined variables that are used as keys when storing edge specific data in the edge attribute dicts
    edge_length_attribute_name = "edge_length"

    def __init__(self, newick=None, newick_format=1, dist=DEFAULT_EDGE_LENGTH, leaf_wrapper=BGGenome):
        self.tree = Tree(newick=newick, format=newick_format, dist=dist)
        self.__root = self.tree
        self.__leaf_wrapper = leaf_wrapper  # a callable, that would be called with leaf name as an argument for Multicolor class
        self.multicolors_are_up_to_date = False
        self.__tree_consistent_multicolors_set = {Multicolor().hashable_representation}
        self.__tree_consistent_multicolors = [Multicolor()]
        self.__vtree_consistent_multicolors_set = {Multicolor().hashable_representation}
        self.__vtree_consistent_multicolors = [Multicolor()]

    def nodes(self):
        """ Proxies iteration to the underlying Tree.iter_descendants iterator, but first yielding a root element

        :return: iterator over all descendants of a root, starting with a root, in current tree
        :rtype: iterator
        """
        yield self.__root
        for entry in self.__root.iter_descendants():
            yield entry

    def edges(self):
        """

        :return: iterator over edges in current tree.
        :rtype: iterator
        """
        if self.__root is None:
            return
        nodes = deque([self.__root])
        while len(nodes) > 0:
            current_node = nodes.popleft()
            if current_node.is_leaf():
                continue
            else:
                for child in current_node.children:
                    yield current_node, child if not child.is_leaf() else self.__leaf_wrapper(child.name)
                    if not child.is_leaf():
                        nodes.append(child)

    def add_edge(self, node1_name, node2_name, edge_length=DEFAULT_EDGE_LENGTH):
        """ Adds a new edge to the current tree with specified characteristics

        Forbids addition of an edge, if a parent node is not present
        Forbids addition of an edge, if a child node already exists

        :param node1_name: name of the parent node, to which an edge shall be added
        :param node2_name: name of newly added child node
        :param edge_length: a length of specified edge
        :return: nothing, inplace changes
        :raises: ValueError (if parent node IS NOT present in the tree, or child node IS already present in the tree)
        """
        if not self.__has_node(name=node1_name):
            raise ValueError("Can not add an edge to a non-existing node {name}".format(name=node1_name))
        if self.__has_node(name=node2_name):
            raise ValueError("Can not add an edge to already existing node {name}".format(name=node2_name))
        self.multicolors_are_up_to_date = False
        self.__get_node_by_name(name=node1_name).add_child(name=node2_name, dist=edge_length)

    def get_node_by_name(self, name):
        """ Proxies the call to the __get_node_by_name method """
        return self.__get_node_by_name(name=name)

    def __get_node_by_name(self, name):
        """ Returns a first TreeNode object, which name matches the specified argument

        :raises: ValueError (if no node with specified name is present in the tree)
        """
        try:
            for entry in filter(lambda x: x.name == name, self.nodes()):
                return entry
        except StopIteration:
            raise ValueError("Attempted to retrieve a non-existing tree node with name: {name}"
                             "".format(name=name))

    def __has_edge(self, node1_name, node2_name, account_for_direction=True):
        """ Returns a boolean flag, telling if a tree has an edge with two nodes, specified by their names as arguments

        If a account_for_direction is specified as True, the order of specified node names has to relate to parent - child relation,
        otherwise both possibilities are checked
        """
        try:
            p1 = self.__get_node_by_name(name=node1_name)
            wdir = node2_name in (node.name for node in p1.children)
            if account_for_direction:
                return wdir
            else:
                p2 = self.__get_node_by_name(name=node2_name)
                return wdir or node1_name in (node.name for node in p2.children)
        except ValueError:
            return False

    def has_edge(self, node1_name, node2_name, account_for_direction=True):
        """ Proxies a call to the __has_edge method """
        return self.__has_edge(node1_name=node1_name, node2_name=node2_name, account_for_direction=account_for_direction)

    def __has_node(self, name):
        """ Check is the current Tree has a node, matching by name to the specified argument """
        result = self.__get_node_by_name(name=name)
        return result is not None

    def has_node(self, name):
        """ Proxies a call to __has_node method """
        return self.__has_node(name=name)

    @property
    def root(self):
        """ A property based call for the root pointer in current tree """
        return self.__root

    def get_distance(self, node1_name, node2_name):
        """ Returns a length of an edge / path, if exists, from the current tree

        :param node1_name: a first node name in current tree
        :param node2_name: a second node name in current tree
        :return: a length of specified by a pair of vertices edge / path
        :rtype: `Number`
        :raises: ValueError, if requested a length of an edge, that is not present in current tree
        """
        return self.__root.get_distance(target=node1_name, target2=node2_name)

    def __vertex_is_leaf(self, node_name):
        """ Checks if a node specified by its name as an argument is a leaf in the current Tree

        :raises: ValueError (if no node with specified name is present in the tree)
        """
        return self.__get_node_by_name(name=node_name).is_leaf()

    def __get_v_tree_consistent_leaf_based_hashable_multicolors(self):
        """ Internally used method, that recalculates VTree-consistent sets of leaves in the current tree """
        result = []
        nodes = deque([self.__root])
        while len(nodes) > 0:
            current_node = nodes.popleft()
            children = current_node.children
            nodes.extend(children)
            if not current_node.is_leaf():
                leaves = filter(lambda node: node.is_leaf(), current_node.get_descendants())
                result.append(Multicolor(*[self.__leaf_wrapper(leaf.name) for leaf in leaves]))
            else:
                result.append(Multicolor(self.__leaf_wrapper(current_node.name)))
        result.append(Multicolor())
        return result

    def get_tree_consistent_multicolors(self):
        """ Returns a copy of the list of T-consistent multicolors from current tree """
        return deepcopy(self.tree_consistent_multicolors)

    def get_vtree_consistent_multicolors(self):
        """ Returns a copy of the list of VT-consistent multicolors from current tree """
        return deepcopy(self.vtree_consistent_multicolors)

    def __update_consistent_multicolors(self):
        """ Internally used method, that recalculates T-consistent / VT-consistent multicolors for current tree topology
        """
        v_t_consistent_multicolors = self.__get_v_tree_consistent_leaf_based_hashable_multicolors()

        hashed_vtree_consistent_leaves_multicolors = {mc.hashable_representation for mc in v_t_consistent_multicolors}
        self.vtree_consistent_multicolors_set = hashed_vtree_consistent_leaves_multicolors
        self.vtree_consistent_multicolors = [Multicolor(*hashed_multicolor) for hashed_multicolor in
                                             hashed_vtree_consistent_leaves_multicolors]
        result = []
        # T-consistent multicolors can be viewed as VT-consistent multicolors united with all of their complements
        full_multicolor = v_t_consistent_multicolors[0]
        for multicolor in v_t_consistent_multicolors:
            result.append(multicolor)
            result.append(full_multicolor - multicolor)

        hashed_tree_consistent_leaves_multicolors = {mc.hashable_representation for mc in result}
        self.tree_consistent_multicolors_set = hashed_tree_consistent_leaves_multicolors
        self.tree_consistent_multicolors = [Multicolor(*hashed_multicolor) for hashed_multicolor in
                                            hashed_tree_consistent_leaves_multicolors]
        self.multicolors_are_up_to_date = True

    @property
    def tree_consistent_multicolors(self):
        """ Property based getter, that checks for consistency in terms of precomputed T-consistent multicolors,
         recomputes all consistent multicolors if tree topology has changed and returns internally stored list of T-consistent multicolors

        """
        if not self.multicolors_are_up_to_date:
            self.__update_consistent_multicolors()
        return self.__tree_consistent_multicolors

    @property
    def tree_consistent_multicolors_set(self):
        """ Property based getter, that checks for consistency in terms of precomputed T-consistent multicolors,
            recomputes all consistent multicolors if tree topology has changed and returns internally stored set of hashable
            representation of T-consistent multicolors

        """
        if not self.multicolors_are_up_to_date:
            self.__update_consistent_multicolors()
        return self.__tree_consistent_multicolors_set

    @tree_consistent_multicolors.setter
    def tree_consistent_multicolors(self, value):
        self.__tree_consistent_multicolors = value

    @tree_consistent_multicolors_set.setter
    def tree_consistent_multicolors_set(self, value):
        self.__tree_consistent_multicolors_set = value

    @property
    def vtree_consistent_multicolors(self):
        """ Property based getter, that checks for consistency in terms of precomputed VT-consistent multicolors,
            recomputes all consistent multicolors if tree topology has changed and returns internally stored list of VT-consistent
            multicolors

        """
        if not self.multicolors_are_up_to_date:
            self.__update_consistent_multicolors()
        return self.__vtree_consistent_multicolors

    @property
    def vtree_consistent_multicolors_set(self):
        """ Property based getter, that checks for consistency in terms of precomputed VT-consistent multicolors,
            recomputes all consistent multicolors if tree topology has changed and returns internally stored set of hashable
            representation of VT-consistent multicolors

        """
        if not self.multicolors_are_up_to_date:
            self.__update_consistent_multicolors()
        return self.__vtree_consistent_multicolors_set

    @vtree_consistent_multicolors.setter
    def vtree_consistent_multicolors(self, value):
        self.__vtree_consistent_multicolors = value

    @vtree_consistent_multicolors_set.setter
    def vtree_consistent_multicolors_set(self, value):
        self.__vtree_consistent_multicolors_set = value

    def multicolor_is_tree_consistent(self, multicolor):
        """ Checks is supplied multicolor is T-consistent """
        return multicolor.hashable_representation in self.tree_consistent_multicolors_set

    def multicolor_is_vtree_consistent(self, multicolor):
        """ Checks is supplied multicolor is VT-consistent """
        return multicolor.hashable_representation in self.vtree_consistent_multicolors_set

    def bgedge_is_vtree_consistent(self, bgedge):
        """ Checks is supplied BGEdge (from the perspective of its multicolor is VT-consistent) """
        return self.multicolor_is_vtree_consistent(bgedge.multicolor)

    def bgedge_is_tree_consistent(self, bgedge):
        """ Checks is supplied BGEdge (from the perspective of its multicolor is T-consistent) """
        return self.multicolor_is_tree_consistent(bgedge.multicolor)

    def append(self, node_name, tree, copy=False):
        """ Append a specified tree (represented by a root TreeNode element) to the node, specified by its name

        :param copy: a flag denoting if the appended tree has to be added as is, or is the deepcopy of it has to be used
        :type copy: Boolean
        :raises: ValueError (if no node with a specified name, to which the specified tree has to be appended, is present in the current tree)
        """
        self.multicolors_are_up_to_date = False
        tree_to_append = tree.__root if not copy else deepcopy(tree.__root)
        self.__get_node_by_name(node_name).add_child(tree_to_append)
