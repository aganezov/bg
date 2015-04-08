# -*- coding: utf-8 -*-
from networkx import Graph
import networkx as nx
from bg.genome import BGGenome

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

DEFAULT_BRANCH_LENGTH = 1


class NewickParser(object):
    @staticmethod
    def parse_simple_node(data_string):
        if len(data_string) == 0:
            raise ValueError("Parsed simple node can not be empty")
        if ":" in data_string:
            node_name, str_branch_length = map(lambda s: s.strip(), data_string.split(":"))
            if len(str_branch_length) == 0:
                str_branch_length = str(DEFAULT_BRANCH_LENGTH)
        else:
            node_name = data_string.strip()
            str_branch_length = str(DEFAULT_BRANCH_LENGTH)
        genome = BGGenome(node_name)
        branch_length = int(str_branch_length) if "." not in str_branch_length else float(str_branch_length)
        return genome, branch_length


class Tree(object):
    def __init__(self):
        self.__root = None
        self.graph = Graph()

    def nodes(self, data=False):
        yield from self.graph.nodes_iter(data=data)

    def edges(self, nbunch=None, data=False):
        yield from self.graph.edges_iter(nbunch=nbunch, data=data)

    def add_node(self, node):
        self.graph.add_node(node)

    def add_edge(self, vertex1, vertex2, branch_length=1, wgd_events=0):
        self.graph.add_edge(u=vertex1, v=vertex2, attr_dict={"branch_length": branch_length, "wgd_events_count": wgd_events})

    @property
    def is_valid_tree(self):
        nodes_cnt = self.graph.number_of_nodes()
        edges_cnt = self.graph.number_of_edges()
        if nodes_cnt == 0 and edges_cnt == 0:
            return True
        else:
            return nodes_cnt == edges_cnt + 1 and nx.is_connected(self.graph)

    def has_edge(self, vertex1, vertex2):
        return self.graph.has_edge(u=vertex1, v=vertex2)

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
        return self.graph[vertex1][vertex2].get("branch_length", 1)

    def edge_wgd_count(self, vertex1, vertex2):
        if not self.has_edge(vertex1, vertex2):
            raise ValueError("Specified edge is not present in current Tree")
        return self.graph[vertex1][vertex2].get("wgd_events_count", 0)