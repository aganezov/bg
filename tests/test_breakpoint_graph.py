# -*- coding: utf-8 -*-
from bg.edge import BGEdge
from bg.multicolor import Multicolor
from bg.vertex import BGVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest
from bg.breakpoint_graph import BreakpointGraph


class BreakpointGraphTestCase(unittest.TestCase):
    def test_empty_initialization(self):
        graph = BreakpointGraph()
        self.assertEqual(len(graph.bg), 0)
        self.assertEqual(len(graph.bg.edges()), 0)
        self.assertEqual(len(list(graph.edges())), 0)
        self.assertEqual(len(list(graph.nodes())), 0)

    def test_add_edge_without_multicolor(self):
        with self.assertRaises(TypeError):
            BreakpointGraph().add_edge(vertex1=BGVertex("v1"), vertex2=BGVertex("v2"))

    def test_get_vertex_by_name(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("black")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        self.assertEqual(graph.get_vertex_by_name("v1"), v1)
        self.assertEqual(graph.get_vertex_by_name("v2"), v2)
        self.assertIsNone(graph.get_vertex_by_name("v3"))

    def test_add_edge(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("black")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        self.assertEqual(len(graph.bg), 2)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(graph.bg.edges()), 1)
        self.assertEqual(len(graph.bg.edges(v1)), 1)
        self.assertEqual(graph.bg.edges(v1, data=True)[0][2]["multicolor"], multicolor)
        self.assertEqual(graph.bg.edges(v2, data=True)[0][2]["multicolor"], multicolor)

    def test_add_bgedge(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("black")
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        graph.add_bgedge(bgedge)
        self.assertEqual(len(graph.bg), 2)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(graph.bg.edges()), 1)
        self.assertEqual(len(graph.bg.edges(v1)), 1)
        self.assertEqual(graph.bg.edges(v1, data=True)[0][2]["multicolor"], multicolor)
        self.assertEqual(graph.bg.edges(v2, data=True)[0][2]["multicolor"], multicolor)

    def test_get_edge_by_two_vertices(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        v3 = BGVertex("v3")
        multicolor1 = Multicolor("red")
        multicolor2 = Multicolor("black")
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor1)
        edge2 = BGEdge(vertex1=v1, vertex2=v3, multicolor=multicolor2)
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor1)
        graph.add_edge(vertex1=v1, vertex2=v3, multicolor=multicolor2)
        self.assertEqual(graph.get_edge_by_two_vertices(vertex1=v1, vertex2=v2), edge1)
        self.assertEqual(graph.get_edge_by_two_vertices(vertex1=v2, vertex2=v1), edge1)
        self.assertEqual(graph.get_edge_by_two_vertices(vertex1=v1, vertex2=v3), edge2)
        self.assertEqual(graph.get_edge_by_two_vertices(vertex1=v3, vertex2=v1), edge2)

    def test_get_edges_by_vertex(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        v3 = BGVertex("v3")
        multicolor1 = Multicolor("red")
        multicolor2 = Multicolor("black")
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor1)
        edge2 = BGEdge(vertex1=v1, vertex2=v3, multicolor=multicolor2)
        graph.add_bgedge(edge1)
        graph.add_bgedge(edge2)
        result = list(graph.get_edges_by_vertex(vertex=v1))
        self.assertTrue(edge1 in result)
        self.assertTrue(edge2 in result)

    def test_add_edge_with_already_existing_merge(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("black")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        multicolor2 = Multicolor("green")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor2)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(graph.get_edge_by_two_vertices(vertex1=v1, vertex2=v2).multicolor, multicolor + multicolor2)
        self.assertEqual(graph.get_edge_by_two_vertices(vertex1=v2, vertex2=v1).multicolor, multicolor + multicolor2)
        multicolor3 = Multicolor("black")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor3)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(graph.get_edge_by_two_vertices(vertex1=v1, vertex2=v2).multicolor,
                         multicolor + multicolor2 + multicolor3)
        self.assertEqual(graph.get_edge_by_two_vertices(vertex1=v2, vertex2=v1).multicolor,
                         multicolor + multicolor2 + multicolor3)

    def test_add_edge_with_already_existing_no_merge(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("black")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        multicolor2 = Multicolor("green")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor2, merge=False)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(len(list(graph.edges())), 2)
        edges = list(graph.get_edges_by_vertex(vertex=v1))
        for bgedge in edges:
            self.assertTrue(bgedge.multicolor in [Multicolor("black"), Multicolor("green")])
        edges = list(graph.get_edges_by_vertex(vertex=v2))
        for bgedge in edges:
            self.assertTrue(bgedge.multicolor in [Multicolor("black"), Multicolor("green")])
        multicolor3 = Multicolor("black")
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor3, merge=False)
        graph.add_edge(vertex1=v1, vertex2=v2, multicolor=multicolor3, merge=False)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(len(list(graph.edges())), 4)
        edges = list(graph.get_edges_by_vertex(vertex=v1))
        for bgedge in edges:
            self.assertTrue(bgedge.multicolor in [Multicolor("black"), Multicolor("green")])
        edges = list(graph.get_edges_by_vertex(vertex=v2))
        for bgedge in edges:
            self.assertTrue(bgedge.multicolor in [Multicolor("black"), Multicolor("green")])

    def test_connected_components_iteration(self):
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        v3 = BGVertex("v3")
        v4 = BGVertex("v4")
        multicolor1 = Multicolor("red")
        multicolor2 = Multicolor("black")
        edge1 = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor1)
        edge2 = BGEdge(vertex1=v3, vertex2=v4, multicolor=multicolor2)
        edge3 = BGEdge(vertex1=v1, vertex2=v3, multicolor=multicolor1)
        graph.add_bgedge(edge1)
        graph.add_bgedge(edge2)
        ccs = list(graph.connected_components_subgraphs())
        self.assertEqual(len(ccs), 2)
        for cc in ccs:
            self.assertEqual(len(list(cc.nodes())), 2)
            self.assertEqual(len(list(cc.edges())), 1)
        if v1 in ccs[0].bg:
            self.assertEqual(ccs[0].get_edge_by_two_vertices(vertex1=v1, vertex2=v2), edge1)
            self.assertEqual(ccs[1].get_edge_by_two_vertices(vertex1=v3, vertex2=v4), edge2)
        else:
            self.assertEqual(ccs[1].get_edge_by_two_vertices(vertex1=v1, vertex2=v2), edge1)
            self.assertEqual(ccs[0].get_edge_by_two_vertices(vertex1=v3, vertex2=v4), edge2)
        graph.add_bgedge(edge3)
        ccs2 = list(graph.connected_components_subgraphs())
        self.assertEqual(len(ccs2), 1)
        self.assertEqual(len(list(ccs2[0].nodes())), 4)
        self.assertEqual(len(list(ccs2[0].edges())), 3)
        self.assertEqual(ccs2[0].get_edge_by_two_vertices(vertex1=v1, vertex2=v2), edge1)
        self.assertEqual(ccs2[0].get_edge_by_two_vertices(vertex1=v3, vertex2=v4), edge2)
        self.assertEqual(ccs2[0].get_edge_by_two_vertices(vertex1=v1, vertex2=v3), edge3)

    def test_delete_edge_existing(self):
        # regular case
        # added edge is deleted
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("black")
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        graph.add_bgedge(bgedge)
        graph.delete_edge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        self.assertEqual(len(list(graph.edges())), 0)
        self.assertEqual(len(list(graph.nodes())), 2)
        graph.add_bgedge(bgedge)
        # added edge is deleted with swapping vertices (as we have non-directed edges, they shall be equal in case
        #                                               of swapping vertices)
        graph.delete_edge(vertex1=v2, vertex2=v1, multicolor=multicolor)
        self.assertEqual(len(list(graph.edges())), 0)
        self.assertEqual(len(list(graph.nodes())), 2)
        # case with deleting a full existing portion of multi-edge with colors of multi-degree greater than 1
        multicolor2 = Multicolor("red", "black", "red")
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor2)
        graph.add_bgedge(bgedge)
        multicolor_to_delete = Multicolor("red", "black")
        graph.delete_edge(vertex1=v1, vertex2=v2, multicolor=multicolor_to_delete)
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(list(graph.edges(nbunch=v1))[0].multicolor, Multicolor("red"))
        # case with deleting an existing portion of multi-edge and non-existing portion of multi-edge
        # in this case existing portion must be deleted, while non-existing must be ignored
        graph = BreakpointGraph()
        v3 = BGVertex("v3")
        v4 = BGVertex("v4")
        multicolor3 = Multicolor("red", "black")
        bgedge = BGEdge(vertex1=v3, vertex2=v4, multicolor=multicolor3)
        graph.add_bgedge(bgedge)
        multicolor_to_delete = Multicolor("red", "red", "red")
        graph.delete_edge(vertex1=v3, vertex2=v4, multicolor=multicolor_to_delete)
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(list(graph.edges(nbunch=v3))[0].multicolor, Multicolor("black"))
        # case with deleting only a non-existing portion of existing single edge
        graph = BreakpointGraph()
        v5 = BGVertex("v5")
        v6 = BGVertex("v6")
        multicolor4 = Multicolor("red", "black")
        bgedge = BGEdge(vertex1=v5, vertex2=v6, multicolor=multicolor4)
        graph.add_bgedge(bgedge)
        multicolor_to_delete = Multicolor("yellow", "green", "yellow")
        graph.delete_edge(vertex1=v5, vertex2=v6, multicolor=multicolor_to_delete)
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(list(graph.edges(nbunch=v5))[0].multicolor, Multicolor("black", "red"))
        graph.delete_edge(vertex1=v6, vertex2=v5, multicolor=multicolor_to_delete)
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(list(graph.edges(nbunch=v6))[0].multicolor, Multicolor("black", "red"))

    def test_delete_bgedge_existing(self):
        # regular case
        # added bgedge is deleted
        graph = BreakpointGraph()
        v1 = BGVertex("v1")
        v2 = BGVertex("v2")
        multicolor = Multicolor("black")
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor)
        graph.add_bgedge(bgedge)
        graph.delete_bgedge(bgedge)
        self.assertEqual(len(list(graph.edges())), 0)
        self.assertEqual(len(list(graph.nodes())), 2)
        # added bgedge is deleted with swapping vertices (as we have non-directed edges, they shall be equal in case
        #                                                 of swapping vertices)
        graph.add_bgedge(bgedge)
        bgedge = BGEdge(vertex1=v2, vertex2=v1, multicolor=multicolor)
        graph.delete_bgedge(bgedge)
        self.assertEqual(len(list(graph.edges())), 0)
        self.assertEqual(len(list(graph.nodes())), 2)
        # case with deleting a full existing portion of multi-edge with colors of multi-degree greater than 1
        multicolor2 = Multicolor("red", "black", "red")
        bgedge = BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor2)
        graph.add_bgedge(bgedge)
        multicolor_to_delete = Multicolor("red", "black")
        graph.delete_bgedge(BGEdge(vertex1=v1, vertex2=v2, multicolor=multicolor_to_delete))
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(list(graph.edges(nbunch=v1))[0].multicolor, Multicolor("red"))
        # case with deleting an existing portion of multi-edge and non-existing portion of multi-edge
        # in this case existing portion must be deleted, while non-existing must be ignored
        graph = BreakpointGraph()
        v3 = BGVertex("v3")
        v4 = BGVertex("v4")
        multicolor3 = Multicolor("red", "black")
        bgedge = BGEdge(vertex1=v3, vertex2=v4, multicolor=multicolor3)
        graph.add_bgedge(bgedge)
        multicolor_to_delete = Multicolor("red", "red", "red")
        graph.delete_bgedge(BGEdge(vertex1=v3, vertex2=v4, multicolor=multicolor_to_delete))
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(list(graph.edges(nbunch=v3))[0].multicolor, Multicolor("black"))
        # case with deleting only a non-existing portion of existing single edge
        graph = BreakpointGraph()
        v5 = BGVertex("v5")
        v6 = BGVertex("v6")
        multicolor4 = Multicolor("red", "black")
        bgedge = BGEdge(vertex1=v5, vertex2=v6, multicolor=multicolor4)
        graph.add_bgedge(bgedge)
        multicolor_to_delete = Multicolor("yellow", "green", "yellow")
        graph.delete_bgedge(BGEdge(vertex1=v5, vertex2=v6, multicolor=multicolor_to_delete))
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(list(graph.edges(nbunch=v5))[0].multicolor, Multicolor("black", "red"))
        graph.delete_bgedge(BGEdge(vertex1=v6, vertex2=v5, multicolor=multicolor_to_delete))
        self.assertEqual(len(list(graph.edges())), 1)
        self.assertEqual(len(list(graph.nodes())), 2)
        self.assertEqual(list(graph.edges(nbunch=v6))[0].multicolor, Multicolor("black", "red"))

if __name__ == '__main__':
    unittest.main()
