# -*- coding: utf-8 -*-
from unittest.mock import Mock
from bg import BGEdge, BGVertex, Multicolor
from bg.kbreak import KBreak

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

import unittest


class KBreakTestCase(unittest.TestCase):
    def test_initialization_incorrect_argument_number(self):
        # required
        # initial set of edges in terms of pairs of vertices
        # desired set of edges in terms of pairs of vertices
        # a multicolor to perform such operation on
        mock_vertex = Mock(spec=BGVertex)
        mock_multicolor = Mock(spec=Multicolor)
        with self.assertRaises(ValueError):
            KBreak(start_edges=[(mock_vertex, ), (mock_vertex, mock_vertex)],
                   result_edges=[(mock_vertex, mock_vertex), (mock_vertex, mock_vertex)],
                   multicolor=mock_multicolor)
        with self.assertRaises(ValueError):
            KBreak(start_edges=[(mock_vertex, mock_vertex), (mock_vertex, mock_vertex)],
                   result_edges=[(mock_vertex, ), (mock_vertex, mock_vertex)],
                   multicolor=mock_multicolor)
        with self.assertRaises(ValueError):
            KBreak(start_edges=[(mock_vertex, mock_vertex), (mock_vertex, )],
                   result_edges=[(mock_vertex, ), (mock_vertex, mock_vertex)],
                   multicolor=mock_multicolor)

    def test_valid_kbreak_matching(self):
        # checks that second, out of two supplied sets of edges (in terms of vertices pairs)
        # corresponds to a matching on the same set of vertices
        # and degrees of each vertex have to be preserved
        v1, v2, v3, v4 = BGVertex("v1"), BGVertex("v2"), BGVertex("v3"), BGVertex("v4")
        # regular 2-break
        start_edges = [(v1, v2), (v3, v4)]
        end_edges = [(v1, v3), (v2, v4)]
        self.assertTrue(KBreak.valid_kbreak_matchings(start_edges, end_edges))
        end_edges = [(v1, v3), (v4, v2)]
        # regular 2-break
        self.assertTrue(KBreak.valid_kbreak_matchings(start_edges, end_edges))
        self.assertTrue(KBreak.valid_kbreak_matchings(start_edges, start_edges))
        self.assertTrue(KBreak.valid_kbreak_matchings(end_edges, end_edges))
        # degrees are not consistent
        end_edges = [(v1, v3), (v2, v2)]
        self.assertFalse(KBreak.valid_kbreak_matchings(start_edges, end_edges))
        # degrees are not consistent
        end_edges = [(v1, v3), (v2, v4), (v1, v3)]
        self.assertFalse(KBreak.valid_kbreak_matchings(start_edges, end_edges))
        # degrees are not consistent
        start_edges = [(v1, v2), (v2, v3), (v1, v3)]
        end_edges = [(v1, v2), (v2, v3), (v2, v3)]
        self.assertFalse(KBreak.valid_kbreak_matchings(start_edges, end_edges))
        # valid two break on K3 graph
        end_edges = [(v1, v1), (v2, v2), (v3, v3)]
        self.assertTrue(KBreak.valid_kbreak_matchings(start_edges, end_edges))

    def test_initialization_incorrect_bad_edge_sets(self):
        # case when initialization is overall correct, in terms of cardinality of supplied sets of vertices
        # all arguments are present
        # but supplied edges in terms of vertices do not correspond to correct k-break
        v1, v2, v3, v4 = BGVertex("v1"), BGVertex("v2"), BGVertex("v3"), BGVertex("v4")
        mock_multicolor = Mock(spec=Multicolor)
        start_edges = [(v1, v2), (v3, v4)]
        end_edges = [(v1, v3), (v2, v2)]
        with self.assertRaises(ValueError):
            KBreak(start_edges=start_edges,
                   result_edges=end_edges,
                   multicolor=mock_multicolor)
        end_edges = [(v1, v3), (v2, v4), (v1, v3)]
        with self.assertRaises(ValueError):
            KBreak(start_edges=start_edges,
                   result_edges=end_edges,
                   multicolor=mock_multicolor)
        start_edges = [(v1, v2), (v2, v3), (v1, v3)]
        end_edges = [(v1, v2), (v2, v3), (v2, v3)]
        with self.assertRaises(ValueError):
            KBreak(start_edges=start_edges,
                   result_edges=end_edges,
                   multicolor=mock_multicolor)

    def test_initialization(self):
        v1, v2, v3, v4 = BGVertex("v1"), BGVertex("v2"), BGVertex("v3"), BGVertex("v4")
        mock_multicolor = Mock(spec=Multicolor)
        start_edges = [(v1, v2), (v3, v4)]
        end_edges = [(v1, v3), (v2, v4)]
        kbreak = KBreak(start_edges=start_edges,
                        result_edges=end_edges,
                        multicolor=mock_multicolor)
        self.assertListEqual(kbreak.start_edges, start_edges)
        self.assertListEqual(kbreak.result_edges, end_edges)
        self.assertEqual(kbreak.multicolor, mock_multicolor)

if __name__ == '__main__':
    unittest.main()
