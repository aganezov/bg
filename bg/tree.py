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


class NewickReader(object):
    """ Class that is designed for reading and parsing a slightly restricted Newick based format for tree representation """

    @classmethod
    def unlabeled_node_names(cls):
        """ A special class based generator for generating names for unlabeled non-terminal nodes """
        for int_value in itertools.count(1):
            yield str(int_value)

    @classmethod
    def parse_node(cls, data_string):
        """ Parses a node in a tree, where such node information is represented in a restricted newick format

        :param data_string: a string with non-terminal node information
        :type data_string: `str`
        :return: name of the node and length of an edge leading to it
        :rtype: `str`, Number
        """
        if ":" in data_string:
            node_name, edge_length_str = data_string.split(":")
            node_name = node_name.strip()
            if len(edge_length_str) == 0:
                edge_length_str = str(DEFAULT_EDGE_LENGTH)
        else:
            node_name = data_string.strip()
            edge_length_str = str(DEFAULT_EDGE_LENGTH)
        edge_length = int(edge_length_str) if "." not in edge_length_str else float(edge_length_str)
        return node_name, edge_length

    @classmethod
    def parse_simple_node(cls, data_string):
        """ Parses terminal node in a tree, where such node information is represented in a restricted newick format

        Checks that node name is not empty, as it is a restriction for Phylogenetic tree,
        where all terminal nodes need to be known

        :param data_string: a string with non-terminal node information
        :type data_string: `str`
        :return: name of the node and length of an edge leading to it
        :rtype: `str`, Number
        :raises: `ValueError` in a case when node name is empty
        """
        node_name, edge_length = cls.parse_node(data_string)
        if len(node_name) == 0:
            raise ValueError("Terminal node can't be empty")
        return BGGenome(node_name), edge_length

    @classmethod
    def separate_into_same_level_nodes(cls, data_string):
        """ Method scans supplied string and determines all subtrees listed in it.

        Performs an additional check to make sure, that there is no empty node listed in supplied subtree string

        :param data_string: a string with subtree information
        :type data_string: `str`
        :return: a list of subtrees (including a terminal subtrees of one node)
        :rtype: `list[str]`
        :raises: ValueError in case when some internal terminal node subtree is empty
        """

        # first cutting point is the beginning of the string
        current_level_separation_comas = [-1]
        overall_result = []
        parenthesis_count = 0
        for cnt, letter in enumerate(data_string):
            ################################################################################################
            #
            # we must be sure, that we count parenthesis, as only top level comas count for separation purposes
            #
            ################################################################################################
            if letter == "(":
                parenthesis_count += 1
            elif letter == ")":
                parenthesis_count -= 1
            elif parenthesis_count == 0 and letter == ",":
                current_level_separation_comas.append(cnt)

        # last cutting point if the end of the string
        current_level_separation_comas.append(len(data_string))
        if len(current_level_separation_comas) == 2 and current_level_separation_comas[1] == 0:
            ################################################################################################
            #
            # if we have exactly two separation points (this is artificial points of start and end of the string)
            # and the second point is present at the second position, we just return an empty string, as nothing is of interest
            #
            ################################################################################################
            return [""]
        for prev_coma_position, current_comma_position in zip(current_level_separation_comas[:-1],
                                                              current_level_separation_comas[1:]):
            ################################################################################################
            #
            # split the string by top level consecutive comas
            #
            #################################################################################################
            overall_result.append(data_string[prev_coma_position + 1: current_comma_position])

        # make sure no flaking white noise is present
        overall_result = [str_data.strip() for str_data in overall_result]
        if any(map(lambda s: len(s) == 0, overall_result)):
            ################################################################################################
            #
            # we restrict out newick tree to contain emtpy non-terminal nodes, as it is
            #   1) useless
            #   2) messes up with tree topology
            #
            ################################################################################################
            raise ValueError("Empty internal node error")
        return overall_result

    @classmethod
    def is_non_terminal_subtree(cls, data_string):
        """ Check is supplied portion of newick formatted string contains a subtree

        :param data_string: a string ro cast a decision about
        :type data_string: `str`
        :return: an answer, is supplied string contains a subtree, or if it is a terminal node
        :rtype: `Boolean`
        """
        return data_string.startswith("(")

    @classmethod
    def tree_node_separation(cls, data_string):
        """ Separates a subtree info from the information, that determines subtree root node, as well as length of a branch to it

        :param data_string: a string with subtree information in it
        :type data_string: `str`
        :return: a pair of strings, separating subtree info with info about subtrees root
        :rtype: `tuple(str, str)`
        """
        last_parenthesis_position = data_string.rfind(")")
        return data_string[:last_parenthesis_position + 1], data_string[last_parenthesis_position + 1:]

    @classmethod
    def from_string(cls, data_string, tree_root=None, name_generator=None):
        """ Main method that reads supplied string (recursive fashion) with newick formatted tree and returns an instance of BGTree

        Performs several top level checks, when called with a full string
        Overall workflow is implemented with a recursion notion, which terminates at the terminal nodes in newick tree
        All errors, that might be encountered during the parsing and processing are bubbling up from the more special methods
            the only exception is a top level check for only a single tree root

        :param data_string: a full newick tree string
        :type data_string: `str`
        :param tree_root: a name of root of the tree, where currently parsed tree shall be attached to (utilized for subsequent calls)
        :type tree_root: `str`
        :param name_generator: a callable that generates names for internal non-terminal nodes, that are left anonymous
        :type name_generator: `callable`
        :return: BGTree that represents the tree encoded in supplied string
        :rtype: `BGTree`
        """
        #################################
        # flanking white noise is always omitted
        data_string = data_string.strip()
        result_tree = BGTree()
        if name_generator is None:
            # NewickReader class has a class based method, that returns a name generator
            # if non specified in the function argument
            name_generator = cls.unlabeled_node_names()
        top_level = ";" in data_string  # semicolon shall be encountered only once during newick tree parsing
        if top_level:
            # if we are on the very top level, we shall just go forward as with a regular subtree and forget about the semicolon
            data_string = data_string[:-1]
        nodes = cls.separate_into_same_level_nodes(data_string=data_string)
        if top_level and len(nodes) > 1:
            # special check, that makes sure that at the very top level tree has only one node, which is a root
            raise ValueError("Top level can not contain more than one root node")
        for current_level_node_str in nodes:
            if cls.is_non_terminal_subtree(current_level_node_str):
                ################################################################################################
                #
                # if we are in a case, when a subtree on current level is not terminal go recursive about it
                #
                ################################################################################################
                subtree_str, node_str = cls.tree_node_separation(data_string=current_level_node_str)
                subtree_str = subtree_str.strip()[1:-1]  # we have parenthesis
                node_name, edge_length = cls.parse_node(node_str)
                if len(node_name) == 0:
                    ################################################################################################
                    #
                    # internal nodes are allowed to be left blank, thus a dummy placer shall be put as their name
                    #
                    ################################################################################################
                    node_name = next(name_generator)
                result_tree.add_node(node_name)
                if top_level:
                    ################################################################################################
                    #
                    # if we are at the very top level, root shall be set to the only node there
                    #
                    ################################################################################################
                    result_tree.root = node_name
                ################################################################################################
                #
                # recursively parse the subtree, specifying that all that subtree shall be appended to subtree root
                #
                ################################################################################################
                subtree = cls.from_string(data_string=subtree_str, tree_root=node_name, name_generator=name_generator)
                ################################################################################################
                #
                # since we've specified a root node name for the subtree parsing, we will get a tree, that has that node in it
                # thus tree appending will be performed against this subtree root node
                #
                ################################################################################################
                result_tree.append(subtree)
                if not top_level:
                    ################################################################################################
                    #
                    # if we are not at the top level, we must attach every current level subtree to the specified root
                    # to get a valid tree at the end
                    #
                    ################################################################################################
                    result_tree.add_edge(vertex1=node_name, vertex2=tree_root, edge_length=edge_length)
            else:
                ################################################################################################
                #
                # we encounter the case, when we hit a terminal level subtree (only a single node there)
                #
                ################################################################################################
                genome, edge_length = cls.parse_simple_node(current_level_node_str)
                if top_level:
                    ################################################################################################
                    #
                    # we are in a very special case situation when a tree is a single node
                    #
                    ################################################################################################
                    result_tree.add_node(genome)
                    result_tree.root = genome
                else:
                    ################################################################################################
                    #
                    # make sure we also attach it to the specified root node
                    #
                    ################################################################################################
                    result_tree.add_edge(vertex1=genome, vertex2=tree_root, edge_length=edge_length)
        return result_tree


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
