# -*- coding: utf-8 -*-
import itertools
from networkx import Graph
import networkx as nx
from bg.genome import BGGenome

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

DEFAULT_BRANCH_LENGTH = 1


class NewickReader(object):

    @classmethod
    def unlabeled_node_names(cls):
        for int_value in itertools.count(1):
            yield str(int_value)

    @classmethod
    def parse_node(cls, data_string):
        if ":" in data_string:
            node_name, branch_length_str = data_string.split(":")
            node_name = node_name.strip()
            if len(branch_length_str) == 0:
                branch_length_str = str(DEFAULT_BRANCH_LENGTH)
        else:
            node_name = data_string.strip()
            branch_length_str = str(DEFAULT_BRANCH_LENGTH)
        branch_length = int(branch_length_str) if "." not in branch_length_str else float(branch_length_str)
        return node_name, branch_length

    @classmethod
    def parse_simple_node(cls, data_string):
        node_name, branch_length = cls.parse_node(data_string)
        if len(node_name) == 0:
            raise ValueError("Terminal node can't be empty")
        return BGGenome(node_name), branch_length

    @classmethod
    def separate_into_same_level_nodes(cls, data_string):
        current_level_separation_comas = [-1]
        overall_result = []
        parenthesis_count = 0
        for cnt, letter in enumerate(data_string):
            if letter == "(":
                parenthesis_count += 1
            elif letter == ")":
                parenthesis_count -= 1
            elif parenthesis_count == 0 and letter == ",":
                current_level_separation_comas.append(cnt)
        current_level_separation_comas.append(len(data_string))
        if len(current_level_separation_comas) == 2 and current_level_separation_comas[1] == 0:
            return [""]
        for prev_coma_position, current_comma_position in zip(current_level_separation_comas[:-1],
                                                              current_level_separation_comas[1:]):
            overall_result.append(data_string[prev_coma_position + 1: current_comma_position])
        overall_result = [str_data.strip() for str_data in overall_result]
        if any(map(lambda s: len(s) == 0, overall_result)):
            raise ValueError("Empty internal node error")
        return overall_result

    @classmethod
    def is_non_terminal_subtree(cls, data_string):
        return data_string.startswith("(")

    @classmethod
    def tree_node_separation(cls, data_string):
        last_parenthesis_position = data_string.rfind(")")
        return data_string[:last_parenthesis_position + 1], data_string[last_parenthesis_position + 1:]

    @classmethod
    def from_string(cls, data_string, tree_root=None, name_generator=None):
        data_string = data_string.strip()
        result_tree = BGTree()
        if name_generator is None:
            name_generator = cls.unlabeled_node_names()
        top_level = ";" in data_string
        if top_level:
            data_string = data_string[:-1]
        nodes = cls.separate_into_same_level_nodes(data_string=data_string)
        if top_level and len(nodes) > 1:
            raise ValueError("Top level can not contain more than one root node")
        for current_level_node_str in nodes:
            if cls.is_non_terminal_subtree(current_level_node_str):
                subtree_str, node_str = cls.tree_node_separation(data_string=current_level_node_str)
                subtree_str = subtree_str.strip()[1:-1]
                node_name, branch_length = cls.parse_node(node_str)
                if len(node_name) == 0:
                    node_name = next(name_generator)
                result_tree.add_node(node_name)
                if top_level:
                    result_tree.root = node_name
                subtree = cls.from_string(data_string=subtree_str, tree_root=node_name, name_generator=name_generator)
                result_tree.append(subtree)
                if not top_level:
                    result_tree.add_edge(vertex1=node_name, vertex2=tree_root, branch_length=branch_length)
            else:
                genome, branch_length = cls.parse_simple_node(current_level_node_str)
                if top_level:
                    # we are in a very special case situation when a tree is a single node
                    result_tree.add_node(genome)
                    result_tree.root = genome
                else:
                    result_tree.add_edge(vertex1=genome, vertex2=tree_root, branch_length=branch_length)
        return result_tree


class BGTree(object):

    wgd_events_count_attribute_name = "wgd_events_count"
    branch_length_attribute_name = "branch_length"

    def __init__(self):
        self.__root = None
        self.graph = Graph()

    def nodes(self, data=False):
        yield from self.graph.nodes_iter(data=data)

    def edges(self, nbunch=None, data=False):
        yield from self.graph.edges_iter(nbunch=nbunch, data=data)

    def add_node(self, node):
        self.graph.add_node(node)

    def __set_wgd_count(self, vertex1, vertex2, wgd_count):
        if not self.has_edge(vertex1=vertex1, vertex2=vertex2):
            raise ValueError("Whole genome duplication count can be assigned only to existing edges")
        if not isinstance(wgd_count, int):
            raise ValueError("Only integer values can be assigned as a whole genome duplication count for tree edges")
        self.graph[vertex1][vertex2][self.wgd_events_count_attribute_name] = wgd_count

    def set_wgd_count(self, vertex1, vertex2, wgd_count):
        self.__set_wgd_count(vertex1=vertex1, vertex2=vertex2, wgd_count=wgd_count)

    def add_edge(self, vertex1, vertex2, branch_length=1, wgd_events=0):
        self.graph.add_edge(u=vertex1, v=vertex2, attr_dict={"branch_length": branch_length})
        self.__set_wgd_count(vertex1=vertex1, vertex2=vertex2, wgd_count=wgd_events)

    @property
    def is_valid_tree(self):
        nodes_cnt = self.graph.number_of_nodes()
        edges_cnt = self.graph.number_of_edges()
        if nodes_cnt == 0 and edges_cnt == 0:
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
        return self.__root

    @root.setter
    def root(self, value):
        if value not in self.graph:
            raise ValueError("Only existing node can be set as root")
        self.__root = value

    def append(self, tree):
        self.graph.add_edges_from(tree.graph.edges_iter(data=True))

    def edge_length(self, vertex1, vertex2):
        if not self.has_edge(vertex1, vertex2):
            raise ValueError("Specified edge is not present in current Tree")
        return self.graph[vertex1][vertex2].get(self.branch_length_attribute_name, 1)

    def edge_wgd_count(self, vertex1, vertex2):
        if not self.__has_edge(vertex1, vertex2):
            raise ValueError("Specified edge is not present in current Tree")
        return self.graph[vertex1][vertex2].get(self.wgd_events_count_attribute_name, 0)