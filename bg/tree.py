# -*- coding: utf-8 -*-
from networkx import Graph
import networkx as nx

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


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

    def add_edge(self, vertex1, vertex2):
        self.graph.add_edge(u=vertex1, v=vertex2)

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