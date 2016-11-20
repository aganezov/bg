# -*- coding: utf-8 -*-
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from bg.kbreak import KBreak
from bg.multicolor import Multicolor
from bg.vertices import BlockVertex, InfinityVertex

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "production"

import unittest


class KBreakTestCase(unittest.TestCase):
    def setUp(self):
        self.v1 = BlockVertex("v1")
        self.v2 = BlockVertex("v2")
        self.v3 = BlockVertex("v3")
        self.v4 = BlockVertex("v4")
        self.inf_v1 = InfinityVertex("v1")
        self.inf_v2 = InfinityVertex("v2")
        self.inf_v3 = InfinityVertex("v3")
        self.inf_v4 = InfinityVertex("v4")

    def test_initialization_incorrect_argument_number(self):
        # required
        # initial set of edges in terms of pairs of vertices
        # desired set of edges in terms of pairs of vertices
        # a multicolor to perform such operation on
        mock_vertex = Mock(spec=BlockVertex)
        mock_multicolor = Mock(spec=Multicolor)
        with self.assertRaises(ValueError):
            KBreak(start_edges=[(mock_vertex,), (mock_vertex, mock_vertex)],
                   result_edges=[(mock_vertex, mock_vertex), (mock_vertex, mock_vertex)],
                   multicolor=mock_multicolor)
        with self.assertRaises(ValueError):
            KBreak(start_edges=[(mock_vertex, mock_vertex), (mock_vertex, mock_vertex)],
                   result_edges=[(mock_vertex,), (mock_vertex, mock_vertex)],
                   multicolor=mock_multicolor)
        with self.assertRaises(ValueError):
            KBreak(start_edges=[(mock_vertex, mock_vertex), (mock_vertex,)],
                   result_edges=[(mock_vertex,), (mock_vertex, mock_vertex)],
                   multicolor=mock_multicolor)

    def test_valid_kbreak_matching(self):
        # checks that second, out of two supplied sets of edges (in terms of vertices pairs)
        # corresponds to a matching on the same set of vertices
        # and degrees of each vertex have to be preserved
        v1, v2, v3, v4 = self.v1, self.v2, self.v3, self.v4
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
        v1, v2, v3, v4 = self.v1, self.v2, self.v3, self.v4
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
        # a correct case of a kbreak initialization, where all correctness checks are successfully passed
        v1, v2, v3, v4 = self.v1, self.v2, self.v3, self.v4
        mock_multicolor = Mock(spec=Multicolor)
        start_edges = [(v1, v2), (v3, v4)]
        end_edges = [(v1, v3), (v2, v4)]
        kbreak = KBreak(start_edges=start_edges,
                        result_edges=end_edges,
                        multicolor=mock_multicolor)
        self.assertListEqual(kbreak.start_edges, start_edges)
        self.assertListEqual(kbreak.result_edges, end_edges)
        self.assertEqual(kbreak.multicolor, mock_multicolor)
        self.assertDictEqual(kbreak.data, KBreak.create_default_data_dict())

    def test_initialization_with_additional_data(self):
        v1, v2, v3, v4 = self.v1, self.v2, self.v3, self.v4
        mock_multicolor = Mock(spec=Multicolor)
        start_edges = [(v1, v2), (v3, v4)]
        end_edges = [(v1, v3), (v2, v4)]
        data = {"origin": None}
        kbreak = KBreak(start_edges=start_edges,
                        result_edges=end_edges,
                        multicolor=mock_multicolor,
                        data=data)
        self.assertListEqual(kbreak.start_edges, start_edges)
        self.assertListEqual(kbreak.result_edges, end_edges)
        self.assertEqual(kbreak.multicolor, mock_multicolor)
        self.assertDictEqual(kbreak.data, data)


if __name__ == '__main__':
    unittest.main()
