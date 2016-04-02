# -*- coding: utf-8 -*-
from copy import deepcopy
import itertools
from networkx import Graph
import networkx as nx
from bg import Multicolor
from bg.genome import BGGenome

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

# defines a default edge length in phylogenetic tree
DEFAULT_EDGE_LENGTH = 1
# defines a default number of whole genome duplication events that occur on a branch of a phylogenetic tree
DEFAULT_EDGE_WGD_COUNT = 0


class BGTree(object):
    """ Class that is designed to store information about phylogenetic information and relations between multiple genomes

    Class utilizes a networkx Graph object as an internal storage
    This tree can store information about:
        * edge lengths
        * number of whole genome duplication events along certain branches
    """

    # class defined variables that are used as keys when storing edge specific data in the edge attribute dicts
    wgd_events_count_attribute_name = "wgd_events_count"
    edge_length_attribute_name = "edge_length"

    def __init__(self):
        self.__root = None
        self.graph = Graph()
        self.multicolors_are_up_to_date = True
        self.__consistent_multicolors_set = {Multicolor().hashable_representation}
        self.__consistent_multicolors = [Multicolor()]
        self.account_for_wgd = False
        self.__prev_account_for_wgd = False
        self.__prev_rooted = False

    def nodes(self, data=False):
        """ Proxies iteration to the underlying networkx.Graph.nodes iterator

        :param data: a flag to indicate if only nodes are required as iteration result, or associated with them additional data as well
        :type data: `Boolean`
        :return: iterator over all nodes in current tree
        :rtype: iterator
        """
        yield from self.graph.nodes_iter(data=data)

    def edges(self, nbunch=None, data=False):
        """ Proxies iteration to the underlying networkx.Graph.edges iterator

        :param nbunch: an optional parameter to iterate over edges incident to specific set of vertices
        :param data: a flag to indicate if only edges are required as iteration result, or associated with them additional data as well
        :return: iterator over edges in current tree
        :rtype: iterator
        """
        yield from self.graph.edges_iter(nbunch=nbunch, data=data)

    def add_node(self, node):
        """ Adds a new node to current graph
        """
        self.graph.add_node(node)
        self.multicolors_are_up_to_date = False

    def __set_wgd_count(self, vertex1, vertex2, wgd_count):
        """ Explicit method to update a number of wgd events associate with current edge (defined by a pair of vertices)

        :param vertex1: a first vertex in current tree an edge is incident to
        :param vertex2: a second vertex in current tree an edge is incident to
        :param wgd_count: a new value of the number of whole genome duplication events associated with current tree edge
        :type wgd_count: `int`
        :return: nothing, inplace changes
        """
        if not self.has_edge(vertex1=vertex1, vertex2=vertex2):
            raise ValueError("Whole genome duplication count can be assigned only to existing edges")
        if not isinstance(wgd_count, int):
            raise ValueError("Only integer values can be assigned as a whole genome duplication count for tree edges")
        self.graph[vertex1][vertex2][self.wgd_events_count_attribute_name] = wgd_count
        self.multicolors_are_up_to_date = False

    def set_wgd_count(self, vertex1, vertex2, wgd_count):
        """ Subclass safe method for explicit wgd setting, that proxies a call to __set_wgd_count """
        self.__set_wgd_count(vertex1=vertex1, vertex2=vertex2, wgd_count=wgd_count)

    def __set_edge_length(self, vertex1, vertex2, edge_length):
        """ Explicit method to update a length value associated with a specific edge

        :param vertex1: a first vertex in current tree an edge is incident to
        :param vertex2: a second vertex in current tree an edge is incident to
        :param edge_length: a new value of edge length
        :type edge_length: `Number`
        :return: nothing, inplace changes
        :raises: ValueError is the edge to update is not present in current graph
        """
        if not self.has_edge(vertex1=vertex1, vertex2=vertex2):
            raise ValueError("Whole genome duplication count can be assigned only to existing edges")
        self.graph[vertex1][vertex2][self.edge_length_attribute_name] = edge_length

    def set_edge_length(self, vertex1, vertex2, edge_length):
        """ Subclass safe method for explicit edge length setting, that proxies a call to __set_edge_length """
        self.__set_edge_length(vertex1=vertex1, vertex2=vertex2, edge_length=edge_length)

    def add_edge(self, vertex1, vertex2, edge_length=DEFAULT_EDGE_LENGTH, wgd_events=DEFAULT_EDGE_WGD_COUNT):
        """ Adds a enw edge to the current tree with specified characteristics

        Due to networkx.Graph.add_edge method, if vertices, that the edge is specified by are not present in current tree,
        they are added automatically

        Can be used (but not advised against) to update existing edge parameters.

        :param vertex1: a first vertex in current tree an edge is incident to
        :param vertex2: a second vertex in current tree an edge is incident to
        :param edge_length: a length of specified edge
        :param wgd_events: a number of whole genome duplication event associated with current edge
        :return: nothing, inplace changes
        """
        self.graph.add_edge(u=vertex1, v=vertex2)
        self.__set_wgd_count(vertex1=vertex1, vertex2=vertex2, wgd_count=wgd_events)
        self.__set_edge_length(vertex1=vertex1, vertex2=vertex2, edge_length=edge_length)
        self.multicolors_are_up_to_date = False

    @property
    def is_valid_tree(self):
        """ A property like check, to make sure current tree is actually valid

        A tree is called valid if it is a connected graph, in which the number_of_nodes equal to the (number_of_edges + 1)
        """
        nodes_cnt = self.graph.number_of_nodes()
        edges_cnt = self.graph.number_of_edges()
        if nodes_cnt == 0 and edges_cnt == 0:
            ################################################################################################
            #
            # empty tree is special case of a valid tree
            #
            ################################################################################################
            return True
        else:
            return nodes_cnt == edges_cnt + 1 and nx.is_connected(self.graph)

    def __has_edge(self, vertex1, vertex2):
        return self.graph.has_edge(u=vertex1, v=vertex2)

    def has_edge(self, vertex1, vertex2):
        return self.__has_edge(vertex1=vertex1, vertex2=vertex2)

    def has_node(self, vertex):
        return self.graph.has_node(n=vertex)

    @property
    def root(self):
        """ A property based call for the root pointer in current tree """
        return self.__root

    @root.setter
    def root(self, value):
        """ A setter for root, that allows root setting only for existing node in the tree, or None """
        if value is not None and value not in self.graph:
            raise ValueError("Only existing node can be set as root")
        self.__root = value
        self.multicolors_are_up_to_date = False

    def append(self, tree):
        """ Append a specified tree, to a current one in a fashion of taken union of edges and vertices between two trees

        Updated current tree with new information
        Utilizes a networkx.Graph method to transparently add info with data (if any) from supplied tree to surrent one

        :param tree: a tree instance to incorporate information from
        :return: nothing, inplace changes
        """
        self.graph.add_edges_from(tree.graph.edges_iter(data=True))
        self.multicolors_are_up_to_date = False

    def edge_length(self, vertex1, vertex2):
        """ Returns a length of an edge, if exists, from the current tree

        :param vertex1: a first vertex in current tree an edge is incident to
        :param vertex2: a second vertex in current tree an edge is incident to
        :return: a length of specified by a pair of vertices edge
        :rtype: `Number`
        :raises: ValueError, if requested a length of an edge, that is not present in current tree
        """
        if not self.has_edge(vertex1, vertex2):
            raise ValueError("Specified edge is not present in current Tree")
        return self.graph[vertex1][vertex2].get(self.edge_length_attribute_name, DEFAULT_EDGE_LENGTH)

    def edge_wgd_count(self, vertex1, vertex2):
        """ Returns a number of wgd events associated with an edge, if exists, from the current tree

        :param vertex1: a first vertex in current tree an edge is incident to
        :param vertex2: a second vertex in current tree an edge is incident to
        :return: a number of wgd events associated with an edge of specified by a pair of vertices
        :rtype: `int`
        :raises: ValueError, if requested a length of an edge, that is not present in current tree
        """
        if not self.__has_edge(vertex1, vertex2):
            raise ValueError("Specified edge is not present in current Tree")
        return self.graph[vertex1][vertex2].get(self.wgd_events_count_attribute_name, DEFAULT_EDGE_WGD_COUNT)

    def __vertex_is_leaf(self, vertex):
        """ Check is there is only a single edge going from a node, which makes it a tree leaf """
        return vertex in self.graph and len(list(self.graph.edges(nbunch=vertex))) <= 1

    def __get_tree_consistent_vertex_based_hashable_multicolors(self, vertex, parent, account_for_wgd=True):
        """ Traverses a tree in a recursive fashion and obtains all possible subtrees composition

        A color is called tree consistent, if it corresponds to some connected part of a tree
        If one takes whole genome duplication events into account, then colors have to be taken to respective powers of two,
         when connected subtree is observed.

        :param vertex: a root of traversed tree
        :param parent: a parent to current traversed tree root
        :param account_for_wgd: a flag, weather to take whole genome duplication into account, ot not
        :return: a list of tree consistent colors for supplied tree
        """

        #########################################################################################################
        #
        # traverse all nodes achievable for current subtree root, if they are not roots parent
        #
        #########################################################################################################
        descendants = [(v1, v2) for v1, v2 in self.graph.edges(vertex) if v1 != parent and v2 != parent]
        result = []
        #########################################################################################################
        #
        # we in the terminal node, and we shall add a single color to the result
        # the only exception is when we take whole genome duplication events into account and the overall
        #   traversal has started from a terminal node, then it shall not be added into the result multicolors set
        #
        #########################################################################################################
        if self.__vertex_is_leaf(vertex=vertex):
            if account_for_wgd:
                if parent is not None:
                    result.append(Multicolor(vertex))
            else:
                result.append(Multicolor(vertex))
        if len(descendants) > 0:
            #########################################################################################################
            #
            # if we are in the internal node, we initialize current vertex multicolor as empty one
            # otherwise we say that current vertex multicolor is the vertex itself
            #   (possible when we don't take wgd events into consideration and start from a leaf)
            #
            #########################################################################################################
            current_vertex_multicolor = Multicolor() if not self.__vertex_is_leaf(vertex) else Multicolor(vertex)
            for v1, v2 in descendants:
                #########################################################################################################
                #
                # recursively iterate over all descending form current subtree root subtrees
                #
                #########################################################################################################
                child_multicolor = self.__get_tree_consistent_vertex_based_hashable_multicolors(vertex=v2, parent=v1,
                                                                                                account_for_wgd=account_for_wgd)
                #########################################################################################################
                #
                # retrieve a number of whole genome duplication events associated with each descenging subtree
                #
                #########################################################################################################
                edge_wgd_count = self.edge_wgd_count(vertex1=v1, vertex2=v2) if account_for_wgd else 0
                #########################################################################################################
                #
                # append result from recursively traversed subtree to current vertex
                #
                #########################################################################################################
                result.extend(child_multicolor)
                for i in range(1, edge_wgd_count + 1):
                    #########################################################################################################
                    #
                    # if we take whole genome duplications into account, we shall append not just a single case of
                    # descendant subtree root multicolor, but all possible powers of two, for each wgd event on respective edge
                    #
                    #########################################################################################################
                    result.append(child_multicolor[-1] * (2 ** i))
                current_vertex_multicolor += child_multicolor[-1] * (2 ** edge_wgd_count)
            result.append(current_vertex_multicolor)
        return result

    def get_tree_consistent_multicolors(self, rooted=True, account_for_wgd=True):
        """ Checks for basic properties of a request for a consistent multicolors, updates internal values if needed and returns a frech copy of a list of tree consistent multicolors

        :param rooted: a flag to indicate if one want to obtain tree consistent multicolor, assuming tree is rooted somewhere
        :param account_for_wgd: a flag to indicate if whole genome duplication events shall have any impact on tree consistency of multicolors
        :return: a deepcopy of a list of tree consistent multicolors
        :raises: ValueError
        """
        if not self.multicolors_are_up_to_date or rooted != self.__prev_rooted or account_for_wgd != self.__prev_account_for_wgd:
            self.__update_consistet_multicolors(rooted=rooted, account_for_wgd=account_for_wgd)
        self.account_for_wgd = self.__prev_account_for_wgd
        return deepcopy(self.consistent_multicolors)

    def __update_consistet_multicolors(self, rooted=True, account_for_wgd=True):
        """ Updates information about tree consistent multicolors for the tree, that might have been changed

        :param rooted: a flag to indicate if one want to obtain tree consistent multicolor, assuming tree is rooted somewhere
        :param account_for_wgd: a flag to indicate if whole genome duplication events shall have any impact on tree consistency of multicolors
        :return: updates internal values
        :raises: ValueError
        """
        #########################################################################################################
        #
        # whole genome duplication events are directed events, and thus tree traversal direction shall be present
        # such direction is denoted by a root
        # if rooted argument if set to False, but whole genome duplications still shall be taken into account,
        #   or the tree root is set to None, correct tree consistent multicolor can be determined and an error is raised
        #
        #########################################################################################################
        if not rooted and account_for_wgd or rooted and self.root is None:
            raise ValueError("Tree consistent colors, that take whole genome duplication into consideration can not "
                             "be constructed on the unrooted tree")
        #########################################################################################################
        #
        # when we don't account for whole genome duplication events we still need to start from some node
        # but it is irrelevant from which node to start, thus a first possible node is determined as a starting point
        #
        #########################################################################################################
        if not account_for_wgd and self.root is None:
            self.root = next(self.nodes())
        #########################################################################################################
        #
        # get all multicolors starting from current root vertex
        #
        #########################################################################################################
        vertex_based_multicolors = self.__get_tree_consistent_vertex_based_hashable_multicolors(vertex=self.root,
                                                                                                parent=None,
                                                                                                account_for_wgd=account_for_wgd)
        result = []
        #########################################################################################################
        #
        # at the point, where recursive processing of multicolors the overall result will correspond to all possible
        # colors in the provided tree, also known as full Multicolor
        #
        #########################################################################################################
        full_multicolor = vertex_based_multicolors[-1]
        #########################################################################################################
        #
        # for each obtained multicolor we need to make sure we also take its complement into the result
        # as a complement of a tree consistent multicolor is also a tree consistent multicolor
        #
        #########################################################################################################
        for multicolor in vertex_based_multicolors:
            result.append(multicolor)
            supplementary = full_multicolor - multicolor
            #########################################################################################################
            #
            # it is important when we get multicolors taking whole genome duplication events into account and are rooted at a leaf
            # not to take that leaf as a tree consistent multicolor
            #
            #########################################################################################################
            if account_for_wgd and self.__vertex_is_leaf(self.root) and supplementary == Multicolor(self.root):
                continue
            result.append(supplementary)
        #########################################################################################################
        #
        # removing all duplications, as some multicolors we obtained along with their supplementary
        #
        #########################################################################################################
        hashed_vertex_tree_consistent_multicolors = {mc.hashable_representation for mc in result}
        self.consistent_multicolors_set = hashed_vertex_tree_consistent_multicolors
        self.consistent_multicolors = [Multicolor(*hashed_multicolor) for hashed_multicolor in
                                       hashed_vertex_tree_consistent_multicolors]
        self.multicolors_are_up_to_date = True
        self.__prev_account_for_wgd = account_for_wgd
        self.__prev_rooted = rooted

    @property
    def consistent_multicolors(self):
        if not self.multicolors_are_up_to_date or self.account_for_wgd != self.__prev_account_for_wgd or (self.root is not None) != self.__prev_rooted:
            self.__update_consistet_multicolors(rooted=self.root is not None, account_for_wgd=self.account_for_wgd)
        self.account_for_wgd = self.__prev_account_for_wgd
        return self.__consistent_multicolors

    @property
    def consistent_multicolors_set(self):
        if not self.multicolors_are_up_to_date or self.account_for_wgd != self.__prev_account_for_wgd or (self.root is not None) != self.__prev_rooted:
            self.__update_consistet_multicolors(rooted=self.root is not None, account_for_wgd=self.account_for_wgd)
        self.account_for_wgd = self.__prev_account_for_wgd
        return self.__consistent_multicolors_set

    @consistent_multicolors.setter
    def consistent_multicolors(self, value):
        self.__consistent_multicolors = value

    @consistent_multicolors_set.setter
    def consistent_multicolors_set(self, value):
        self.__consistent_multicolors_set = value

    def is_multicolor_consistent(self, multicolor):
        return multicolor.hashable_representation in self.consistent_multicolors_set

    def is_bgedge_consistent(self, bgedge):
        return self.is_multicolor_consistent(bgedge.multicolor)
